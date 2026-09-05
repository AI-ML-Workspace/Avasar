import logging
from typing import Dict, List, Optional, Union

from app.models.chat import SourceItem
from app.models.document import ProcessedChunk
from app.services.llm_providers import LLMProvider, get_llm_provider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are Avasar, a knowledgeable and strictly grounded conversational assistant for Indian Government Welfare Schemes.

CRITICAL OPERATING RULES:
1. Strict Grounding: Answer the citizen's question strictly and exclusively using ONLY the provided Scheme Context below.
2. Zero Hallucination: Do NOT invent scheme details, financial assistance amounts, eligibility rules, application links, or deadlines.
3. No External Assumptions: Do NOT extrapolate beyond the facts directly provided in the context.
4. Conversational Continuity: Use recent conversation history to understand follow-up questions (e.g. pronouns like "it", "they", or elliptical follow-ups like "who is eligible?", "what documents do I need?"). Maintain focus on the active scheme being discussed unless the citizen switches schemes.
5. Eligibility Guidance: When citizens ask whether they qualify, evaluate their details against the retrieved official criteria:
   - If their details meet all criteria, explain their eligibility clearly.
   - If key details are missing (e.g. landholding, age, student category, income), politely identify the specific missing facts needed to determine eligibility.
   - Distinguish between confirmed eligibility, likely eligibility with conditions, and insufficient information.
   - NEVER guarantee official government acceptance; state that final approval is determined by the official implementing agency.
6. Scheme Discovery: When citizens ask for schemes by persona (e.g. students, farmers, women, small business), present the matching verified options found in the retrieved context.
7. Handling Missing Data: If the provided Scheme Context does not contain enough information to answer the question, clearly state: "Based on the verified government scheme records currently available, there is not enough information to answer this question." Do NOT guess or speculate.
8. Tone: Helpful, factual, polite, and accessible to Indian citizens.
"""


def format_sources_context(sources: List[Union[SourceItem, ProcessedChunk]]) -> str:
    """Format retrieved scheme records into a compact, deterministic context block.

    Args:
        sources: List of SourceItem or ProcessedChunk objects retrieved via RAG.

    Returns:
        Structured text block ready for inclusion in the user prompt.
    """
    if not sources:
        return "No relevant scheme context available."

    formatted_docs: List[str] = []
    for idx, item in enumerate(sources, start=1):
        if isinstance(item, SourceItem):
            title = item.title
            url = item.url or "N/A"
            content = item.snippet or ""
        elif isinstance(item, ProcessedChunk):
            title = item.title
            url = item.url or "N/A"
            content = item.text
        else:
            title = getattr(item, "title", "Scheme Document")
            url = getattr(item, "url", "N/A")
            content = getattr(item, "snippet", "") or getattr(item, "text", "")

        formatted_docs.append(
            f"[Source {idx}] Scheme: {title}\n"
            f"Official URL: {url}\n"
            f"Verified Details:\n{content.strip()}"
        )

    return "\n\n---\n\n".join(formatted_docs)


class LLMService:
    """Service for generating grounded scheme answers from retrieved context."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self._provider = provider

    @property
    def provider(self) -> LLMProvider:
        """Configured LLM provider instance."""
        if self._provider is None:
            self._provider = get_llm_provider()
        return self._provider

    async def generate_answer(
        self,
        query: str,
        sources: List[Union[SourceItem, ProcessedChunk]],
        language: str = "en",
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        active_scheme: Optional[str] = None,
    ) -> str:
        """Generate a grounded scheme explanation based on retrieved context and conversation history.

        Args:
            query: Citizen question.
            sources: Verified scheme documents/chunks retrieved from the knowledge base.
            language: Target response language code.
            conversation_id: Optional multi-turn conversation tracker.
            conversation_history: Recent conversational messages for multi-turn context.
            active_scheme: Canonical name of the scheme currently being discussed.

        Returns:
            Generated response string strictly grounded in the provided sources.

        Raises:
            ValueError: If query is empty.
            RuntimeError: If the underlying LLM provider call fails.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty for answer generation.")

        # If no sources were retrieved, return clear grounded fallback without calling LLM
        if not sources:
            return (
                "Based on the verified government scheme records currently available, "
                "no matching scheme details were found for your question."
            )

        context_text = format_sources_context(sources)

        history_block = ""
        if conversation_history:
            history_lines = []
            for turn in conversation_history[-6:]:
                role = "Citizen" if turn.get("role") == "user" else "Avasar"
                history_lines.append(f"{role}: {turn.get('content', '')}")
            history_block = "Recent Conversation History:\n" + "\n".join(history_lines) + "\n\n"

        scheme_focus = f"Active Scheme Focus: {active_scheme}\n\n" if active_scheme else ""

        user_prompt = (
            f"{history_block}"
            f"Scheme Context:\n"
            f"===============\n"
            f"{context_text}\n\n"
            f"{scheme_focus}"
            f"Citizen Question: {query.strip()}\n\n"
            f"Please answer the citizen's question accurately based strictly on the Scheme Context above."
        )

        return await self.provider.generate(
            system_prompt=SYSTEM_PROMPT_TEMPLATE,
            user_prompt=user_prompt,
        )
