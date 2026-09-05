import logging
import re
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.chat import ChatRequest, ChatResponse
from app.services.conversation_store import (
    ConversationStore,
    QueryContextualizer,
    get_conversation_store,
)
from app.services.language_pipeline import LanguagePipeline
from app.services.llm import LLMService
from app.services.rag import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


def get_language_pipeline() -> LanguagePipeline:
    """Dependency provider for LanguagePipeline."""
    return LanguagePipeline()


def get_rag_service() -> RAGService:
    """Dependency provider for RAGService."""
    return RAGService()


def get_llm_service() -> LLMService:
    """Dependency provider for LLMService."""
    return LLMService()


def get_conversation_store_dep() -> ConversationStore:
    """Dependency provider for ConversationStore."""
    return get_conversation_store()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about government schemes",
    description="Accepts a citizen query, language code, and optional conversation ID.",
    responses={
        status.HTTP_200_OK: {
            "description": "Successful conversational answer with verified sources"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation Error (e.g. missing or empty message)"
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service temporarily unable to generate an answer"
        },
    },
)
async def chat_endpoint(
    request: ChatRequest,
    pipeline: LanguagePipeline = Depends(get_language_pipeline),
    rag: RAGService = Depends(get_rag_service),
    llm: LLMService = Depends(get_llm_service),
    store: ConversationStore = Depends(get_conversation_store_dep),
) -> ChatResponse:
    """Conversational chat endpoint with multi-turn memory, follow-up resolution, and language continuity."""
    # 1. Resolve or initialize conversation session
    cid = (
        request.conversation_id.strip()
        if request.conversation_id and request.conversation_id.strip()
        else f"conv_{uuid.uuid4().hex[:12]}"
    )
    session = store.get_or_create_session(conversation_id=cid)

    # 2. Determine effective client language (honoring client preference or maintaining continuity)
    if request.language:
        session.preferred_language = request.language.strip().lower()
        effective_lang = session.preferred_language
    elif session.turns and session.preferred_language != "en":
        effective_lang = session.preferred_language
    else:
        effective_lang = None

    # 3. Inbound normalization and language detection
    processed = await pipeline.process_query(
        text=request.message,
        client_language=effective_lang,
    )

    detected_lang = processed.detected_language
    session.preferred_language = detected_lang

    # 4. Check for ambiguous standalone query without active scheme context
    if QueryContextualizer.is_ambiguous_standalone(
        processed.normalized_query, active_scheme=session.active_scheme
    ):
        clarification_answer = QueryContextualizer.get_clarification_message(detected_lang)
        store.add_turn(
            conversation_id=cid,
            user_message=request.message,
            assistant_answer=clarification_answer,
            detected_language=detected_lang,
            contextualized_query=processed.normalized_query,
            sources=[],
            active_scheme=None,
        )
        return ChatResponse(
            answer=clarification_answer,
            language=detected_lang,
            sources=[],
            conversation_id=cid,
        )

    # 5. Contextualize query if follow-up reference to active scheme exists
    contextualized_query, was_modified = QueryContextualizer.contextualize_query(
        query=processed.normalized_query,
        active_scheme=session.active_scheme,
    )

    # 6. Retrieve relevant scheme sources via RAG
    # For standalone scheme queries (not already-contextualized follow-ups), expand with domain
    # keywords to boost FAISS similarity (e.g. "What is Ayushman Bharat?" → adds PM-JAY terms).
    # For follow-ups (was_modified=True) the scheme + intent term are already in the query and
    # generic expansion would dilute the specific retrieval signal (e.g. "documents").
    if not was_modified:
        retrieval_query = QueryContextualizer.expand_query_for_retrieval(contextualized_query)
    else:
        retrieval_query = contextualized_query
    try:
        sources = await rag.retrieve(query=retrieval_query)
    except Exception as err:
        logger.warning(f"RAG retrieval encountered an error, falling back to empty sources: {err}")
        sources = []

    if not sources and retrieval_query != contextualized_query:
        try:
            sources = await rag.retrieve(query=contextualized_query)
        except Exception as err:
            logger.warning(f"Secondary RAG retrieval encountered an error: {err}")
            sources = []

    if not sources:
        try:
            sources = await rag.retrieve_featured(top_k=4)
        except Exception as err:
            logger.warning(f"Featured schemes retrieval encountered an error: {err}")
            sources = []

    # 7. Generate grounded answer via LLM with conversation history
    try:
        raw_answer = await llm.generate_answer(
            query=contextualized_query,
            sources=sources,
            language="en",
            conversation_id=cid,
            conversation_history=session.get_history_dicts(),
            active_scheme=session.active_scheme,
        )
    except Exception as err:
        logger.error(f"LLM generation failed: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unable to generate an answer. Please try again later.",
        )

    # 8. Outbound localization / translation
    try:
        final_answer = await pipeline.translate_response(
            answer=raw_answer,
            target_language=detected_lang,
        )
    except Exception as err:
        logger.warning(f"Outbound translation failed, falling back to English answer: {err}")
        final_answer = raw_answer

    # 9. Determine active scheme for next conversation turns
    detected_scheme = QueryContextualizer.detect_scheme_in_text(request.message)
    if not detected_scheme and sources:
        detected_scheme = QueryContextualizer.detect_scheme_in_text(sources[0].title)
        if not detected_scheme:
            clean_title = re.sub(
                r"\s+(Official\s+Portal|Portal|Guidelines|Overview|Scheme)$",
                "",
                sources[0].title,
                flags=re.IGNORECASE,
            ).strip()
            detected_scheme = clean_title or sources[0].title
    active_for_turn = detected_scheme or session.active_scheme

    # 10. Record turn in conversation store
    store.add_turn(
        conversation_id=cid,
        user_message=request.message,
        assistant_answer=final_answer,
        detected_language=detected_lang,
        contextualized_query=contextualized_query if was_modified else None,
        sources=sources,
        active_scheme=active_for_turn,
    )

    # 11. Return response adhering strictly to existing API contract
    return ChatResponse(
        answer=final_answer,
        language=detected_lang,
        sources=sources,
        conversation_id=cid,
    )
