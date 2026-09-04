import unittest
from unittest.mock import AsyncMock, patch

from app.services.language_pipeline import LanguagePipeline, ProcessedQuery
from app.services.translation import TranslationService


class TestTranslation(unittest.IsolatedAsyncioTestCase):
    """Focused tests for TranslationService and LanguagePipeline."""

    def setUp(self):
        self.service = TranslationService()

    @patch("httpx.AsyncClient.get")
    async def test_english_fast_path(self, mock_get):
        # English to English should never invoke external API
        text = "How do I apply for PM Kisan scheme?"
        result = await self.service.translate(text, source_lang="en", target_lang="en")
        self.assertEqual(result, text)
        mock_get.assert_not_called()

        result_helper = await self.service.translate_to_english(text, source_lang="en")
        self.assertEqual(result_helper, text)
        mock_get.assert_not_called()

        result_outbound = await self.service.translate_from_english(text, target_lang="en")
        self.assertEqual(result_outbound, text)
        mock_get.assert_not_called()

    @patch("httpx.AsyncClient.get")
    async def test_same_language_fast_path(self, mock_get):
        # Translating to the same language should bypass translation
        text = "पीएम किसान योजना"
        result = await self.service.translate(text, source_lang="hi", target_lang="hi")
        self.assertEqual(result, text)
        mock_get.assert_not_called()

    @patch("httpx.AsyncClient.get")
    async def test_empty_or_whitespace_text_fast_path(self, mock_get):
        self.assertEqual(await self.service.translate("", "hi", "en"), "")
        self.assertEqual(await self.service.translate("   ", "hi", "en"), "   ")
        mock_get.assert_not_called()

    @patch("httpx.AsyncClient.get")
    async def test_translate_to_english_mocked(self, mock_get):
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: [
            [["What is PM Kisan scheme?", "पीएम किसान योजना क्या है?"]]
        ]
        mock_get.return_value = mock_resp

        result = await self.service.translate_to_english(
            "पीएम किसान योजना क्या है?", source_lang="hi"
        )
        self.assertEqual(result, "What is PM Kisan scheme?")
        mock_get.assert_called_once()

    @patch("httpx.AsyncClient.get")
    async def test_translate_from_english_mocked(self, mock_get):
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: [
            [["पीएम किसान ₹6000 प्रदान करता है।", "PM Kisan provides Rs 6000."]]
        ]
        mock_get.return_value = mock_resp

        result = await self.service.translate_from_english(
            "PM Kisan provides Rs 6000.", target_lang="hi"
        )
        self.assertEqual(result, "पीएम किसान ₹6000 प्रदान करता है।")
        mock_get.assert_called_once()

    @patch("httpx.AsyncClient.get", side_effect=Exception("API connection timeout"))
    async def test_translation_failure_graceful_fallback(self, mock_get):
        # Network/API error should never crash chatbot; should fallback to original text
        original = "पीएम किसान योजना"
        result = await self.service.translate(original, source_lang="hi", target_lang="en")
        self.assertEqual(result, original)

    @patch("httpx.AsyncClient.get")
    async def test_translation_non_200_fallback(self, mock_get):
        mock_resp = AsyncMock()
        mock_resp.status_code = 503
        mock_get.return_value = mock_resp

        original = "पीएम किसान योजना"
        result = await self.service.translate(original, source_lang="hi", target_lang="en")
        self.assertEqual(result, original)


class TestLanguagePipeline(unittest.IsolatedAsyncioTestCase):
    """Tests for the end-to-end LanguagePipeline coordinating detection and translation."""

    async def test_process_query_english_fast_path(self):
        pipeline = LanguagePipeline()
        query = "Who is eligible for PM Kisan?"
        processed: ProcessedQuery = await pipeline.process_query(query)

        self.assertEqual(processed.original_text, query)
        self.assertEqual(processed.detected_language, "en")
        self.assertEqual(processed.normalized_query, query)

    @patch("httpx.AsyncClient.get")
    async def test_process_query_indic_language(self, mock_get):
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: [
            [["How much money is given in PM Kisan?", "पीएम किसान में कितने पैसे मिलते हैं?"]]
        ]
        mock_get.return_value = mock_resp

        pipeline = LanguagePipeline()
        hindi_query = "पीएम किसान में कितने पैसे मिलते हैं?"
        processed: ProcessedQuery = await pipeline.process_query(hindi_query)

        self.assertEqual(processed.original_text, hindi_query)
        self.assertEqual(processed.detected_language, "hi")
        self.assertEqual(processed.normalized_query, "How much money is given in PM Kisan?")

    async def test_process_query_with_explicit_client_language(self):
        pipeline = LanguagePipeline()
        # Even if query is mixed, client-specified language is respected
        processed = await pipeline.process_query("PM Kisan", client_language="hi-IN")
        self.assertEqual(processed.detected_language, "hi")

    @patch("httpx.AsyncClient.get")
    async def test_translate_response_indic(self, mock_get):
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: [
            [["पीएम किसान ₹6000 प्रति वर्ष देता है।", "PM Kisan provides Rs 6000 per year."]]
        ]
        mock_get.return_value = mock_resp

        pipeline = LanguagePipeline()
        english_answer = "PM Kisan provides Rs 6000 per year."
        localized = await pipeline.translate_response(english_answer, target_language="hi")

        self.assertEqual(localized, "पीएम किसान ₹6000 प्रति वर्ष देता है।")

    @patch("httpx.AsyncClient.get")
    async def test_translate_response_english_fast_path(self, mock_get):
        pipeline = LanguagePipeline()
        english_answer = "PM Kisan provides Rs 6000 per year."
        localized = await pipeline.translate_response(english_answer, target_language="en")

        self.assertEqual(localized, english_answer)
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
