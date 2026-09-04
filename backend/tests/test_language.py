import unittest
from unittest.mock import AsyncMock, patch

from app.services.language import (
    LanguageService,
    normalize_language_code,
    SUPPORTED_LANGUAGES,
)


class TestLanguageDetection(unittest.IsolatedAsyncioTestCase):
    """Focused tests for language detection and language-code normalization."""

    def setUp(self):
        self.service = LanguageService(default_language="en")

    def test_supported_languages_list(self):
        required = {"en", "hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "pa"}
        self.assertTrue(required.issubset(set(SUPPORTED_LANGUAGES.keys())))

    def test_normalize_language_code(self):
        # Exact ISO codes
        self.assertEqual(normalize_language_code("en"), "en")
        self.assertEqual(normalize_language_code("hi"), "hi")
        self.assertEqual(normalize_language_code("bn"), "bn")

        # Case insensitivity
        self.assertEqual(normalize_language_code("HI"), "hi")
        self.assertEqual(normalize_language_code("EN"), "en")

        # BCP 47 locales
        self.assertEqual(normalize_language_code("hi-IN"), "hi")
        self.assertEqual(normalize_language_code("en_US"), "en")
        self.assertEqual(normalize_language_code("ta-IN"), "ta")

        # Full language names
        self.assertEqual(normalize_language_code("hindi"), "hi")
        self.assertEqual(normalize_language_code("english"), "en")
        self.assertEqual(normalize_language_code("bengali"), "bn")
        self.assertEqual(normalize_language_code("tamil"), "ta")

        # 3-letter ISO 639-2
        self.assertEqual(normalize_language_code("hin"), "hi")
        self.assertEqual(normalize_language_code("eng"), "en")
        self.assertEqual(normalize_language_code("tel"), "te")

        # Unsupported / None / Empty
        self.assertEqual(normalize_language_code(None), "en")
        self.assertEqual(normalize_language_code(""), "en")
        self.assertEqual(normalize_language_code("xyz_unknown"), "en")

    async def test_detect_english(self):
        query = "What is the financial assistance provided under PM-KISAN?"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "en")

    async def test_detect_hindi(self):
        query = "पीएम किसान योजना में कितने पैसे मिलते हैं?"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "hi")

    async def test_detect_bengali(self):
        query = "প্রধানমন্ত্রী কিষাণ যোজনা কী?"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "bn")

    async def test_detect_tamil(self):
        query = "பிரதமர் கிசான் திட்டம் என்றால் என்ன?"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "ta")

    async def test_detect_telugu(self):
        query = "పీఎం కిసాన్ పథకం గురించి చెప్పండి"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "te")

    async def test_detect_marathi(self):
        # Query with distinctive Marathi words (आहे, माहिती, हवी)
        query = "मला पीएम किसान योजनेची माहिती हवी आहे"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "mr")

    async def test_detect_gujarati(self):
        query = "પીએમ કિસાન યોજના શું છે?"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "gu")

    async def test_detect_punjabi(self):
        query = "ਪੀਐਮ ਕਿਸਾਨ ਯੋਜਨਾ ਕੀ ਹੈ?"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "pa")

    async def test_empty_or_whitespace_detection(self):
        self.assertEqual(await self.service.detect_language(""), "en")
        self.assertEqual(await self.service.detect_language("   \n\t  "), "en")

    async def test_unsupported_or_uncertain_language_fallback(self):
        # Completely unknown symbols without Latin/Indic script
        query = "12345 67890 !@#$%^"
        lang = await self.service.detect_language(query)
        self.assertEqual(lang, "en")

    @patch("httpx.AsyncClient.get")
    async def test_online_detection_fallback_mocked(self, mock_get):
        # Mocking API fallback response for non-script-matched queries
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: [[["Kisan Yojana", "Kisan Yojana"]], None, "hi"]
        mock_get.return_value = mock_response

        # Non-script query that delegates to online detection
        lang = await self.service.detect_language("12345 67890 ???")
        self.assertEqual(lang, "hi")

    @patch("httpx.AsyncClient.get", side_effect=Exception("Network connection failed"))
    async def test_online_detection_network_error_graceful_fallback(self, mock_get):
        # Ensure network errors never crash detection
        lang = await self.service.detect_language("12345 67890 ???")
        self.assertEqual(lang, "en")


if __name__ == "__main__":
    unittest.main()
