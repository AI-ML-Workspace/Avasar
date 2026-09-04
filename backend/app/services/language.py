class LanguageService:
    """Service interface for language detection across Indian languages and English."""

    async def detect_language(self, text: str) -> str:
        """Detect the ISO 639-1 language code of the input text.

        Args:
            text: Input text string.

        Returns:
            ISO 639-1 code (e.g. 'hi', 'en', 'bn', 'ta', 'te').
        """
        raise NotImplementedError("Language detection service is not yet implemented.")
