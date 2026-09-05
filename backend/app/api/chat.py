import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.chat import ChatRequest, ChatResponse
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
) -> ChatResponse:
    """Chat endpoint orchestrating language processing, RAG retrieval, and LLM generation.

    Flow:
        1. Language detection and translation of query to English (LanguagePipeline)
        2. Vector search retrieval of relevant scheme sources (RAGService)
        3. Grounded answer generation using retrieved context (LLMService)
        4. Localization of answer back to citizen's language (LanguagePipeline)
        5. Return ChatResponse containing answer, language, sources, and conversation_id
    """
    # 1. Normalize query and detect/confirm language
    processed = await pipeline.process_query(
        text=request.message,
        client_language=request.language,
    )

    # 2. Retrieve relevant scheme context via RAG
    try:
        sources = await rag.retrieve(query=processed.normalized_query)
    except Exception as err:
        logger.warning(f"RAG retrieval encountered an error, falling back to empty sources: {err}")
        sources = []

    # 3. Generate grounded answer via LLM
    try:
        raw_answer = await llm.generate_answer(
            query=processed.normalized_query,
            sources=sources,
            language="en",
            conversation_id=request.conversation_id,
        )
    except Exception as err:
        logger.error(f"LLM generation failed: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unable to generate an answer. Please try again later.",
        )

    # 4. Translate response to target language if not English
    try:
        final_answer = await pipeline.translate_response(
            answer=raw_answer,
            target_language=processed.detected_language,
        )
    except Exception as err:
        logger.warning(f"Outbound translation failed, falling back to English answer: {err}")
        final_answer = raw_answer

    # 5. Return structured response
    return ChatResponse(
        answer=final_answer,
        language=processed.detected_language,
        sources=sources,
        conversation_id=request.conversation_id,
    )
