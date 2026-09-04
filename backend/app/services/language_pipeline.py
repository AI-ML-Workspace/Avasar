from dataclasses import dataclass
from typing import Optional

from app.services.language import LanguageService, normalize_language_code
from app.services.translation import TranslationService


@dataclass
class ProcessedQuery:
    """Result of processing an inbound citizen query."""
    original_text: str
    detected_language: str
    normalized_query: str


class LanguagePipeline:
    """Unified pipeline coordinating language detection and bidirectional translation.

    Encapsulates inbound query normalization (translating to English for RAG/LLM)
    and outbound answer localization (translating back to citizen's language).
    """

    def __init__(
        self,
        language_service: Optional[LanguageService] = None,
        translation_service: Optional[TranslationService] = None,
    ):
        self.language_service = language_service or LanguageService()
        self.translation_service = translation_service or TranslationService()

    async def process_query(
        self,
        text: str,
        client_language: Optional[str] = None,
    ) -> ProcessedQuery:
        """Process inbound query: detect language and translate to English if needed.

        Args:
            text: Raw citizen query string.
            client_language: Optional client-declared language code.

        Returns:
            ProcessedQuery containing original_text, detected_language, and normalized_query.
        """
        clean_text = text.strip() if text else ""

        # Use client-specified language if valid, otherwise auto-detect
        if client_language:
            detected_lang = normalize_language_code(client_language, default="en")
        else:
            detected_lang = await self.language_service.detect_language(clean_text)

        # Inbound translation: translate to English if query is in an Indic language
        if detected_lang != "en" and clean_text:
            normalized_query = await self.translation_service.translate_to_english(
                clean_text, source_lang=detected_lang
            )
        else:
            normalized_query = clean_text

        return ProcessedQuery(
            original_text=clean_text,
            detected_language=detected_lang,
            normalized_query=normalized_query,
        )

    async def translate_response(self, answer: str, target_language: str) -> str:
        """Translate outbound grounded answer from English to citizen's target language.

        Args:
            answer: Grounded scheme answer generated in English.
            target_language: ISO 639-1 code of citizen's language.

        Returns:
            Translated answer string in target language (or original English if target is 'en').
        """
        clean_answer = answer.strip() if answer else ""
        if not clean_answer:
            return ""

        target_code = normalize_language_code(target_language, default="en")
        if target_code == "en":
            return clean_answer

        return await self.translation_service.translate_from_english(
            clean_answer, target_lang=target_code
        )
