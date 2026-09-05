import logging
from typing import Optional
import httpx

from app.services.language import normalize_language_code

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for bidirectional translation between Indian languages and English."""

    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """Translate text between languages.

        Args:
            text: Text to translate.
            source_lang: Source language code (ISO 639-1).
            target_lang: Target language code (ISO 639-1).

        Returns:
            Translated text string (or original text on failure/fast-path).
        """
        # Fast path: Empty or whitespace
        if not text or not text.strip():
            return text

        src = normalize_language_code(source_lang, default="en")
        tgt = normalize_language_code(target_lang, default="en")

        # Fast path: Same language
        if src == tgt:
            return text

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": "gtx",
                        "sl": src,
                        "tl": tgt,
                        "dt": "t",
                        "q": text,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data and isinstance(data[0], list):
                        parts = [
                            segment[0]
                            for segment in data[0]
                            if isinstance(segment, list) and segment and segment[0]
                        ]
                        if parts:
                            return "".join(parts)
                else:
                    logger.warning(
                        f"Translation service returned status {resp.status_code} for {src}->{tgt}"
                    )
        except Exception as err:
            logger.warning(f"Translation request failed ({src}->{tgt}): {err}")

        # Graceful fallback: Never crash the chatbot on translation error
        return text

    async def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate text from source language to English."""
        return await self.translate(text, source_lang=source_lang, target_lang="en")

    async def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate text from English to target language."""
        return await self.translate(text, source_lang="en", target_lang=target_lang)
