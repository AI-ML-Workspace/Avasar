import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.chat import SourceItem
from app.models.document import ProcessedChunk
from app.services.llm import LLMService, SYSTEM_PROMPT_TEMPLATE, format_sources_context
from app.services.llm_providers import (
    GeminiProvider,
    GroqProvider,
    LLMProvider,
    OpenAIProvider,
    get_llm_provider,
)


class MockTestProvider(LLMProvider):
    """Deterministic mock provider for testing LLMService without network calls."""

    def __init__(self, response_text: str = "Mock answer"):
        self.response_text = response_text
        self.last_system_prompt = None
        self.last_user_prompt = None

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature=None,
        max_tokens=None,
    ) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response_text


class TestLLMProviders(unittest.IsolatedAsyncioTestCase):
    """Focused tests for LLM provider adapters, validation, and error handling."""

    def test_unsupported_provider_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            get_llm_provider("unsupported_ai")
        self.assertIn("Unsupported LLM provider", str(ctx.exception))

    def test_missing_api_key_raises_error(self):
        with self.assertRaises(ValueError):
            GroqProvider(api_key="")

        with self.assertRaises(ValueError):
            GeminiProvider(api_key="")

        with self.assertRaises(ValueError):
            OpenAIProvider(api_key="")

    async def test_groq_successful_response(self):
        with patch("groq.AsyncGroq") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = "PM Kisan benefits answer from Groq."
            mock_response.choices = [mock_choice]

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            provider = GroqProvider(api_key="gsk_mock_test_key", model="llama-3.3-70b")
            answer = await provider.generate("System prompt", "User query")

            self.assertEqual(answer, "PM Kisan benefits answer from Groq.")
            mock_client.chat.completions.create.assert_called_once()

    async def test_groq_error_handling(self):
        with patch("groq.AsyncGroq") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("Rate limit exceeded"))

            provider = GroqProvider(api_key="gsk_mock_test_key")
            with self.assertRaises(RuntimeError) as ctx:
                await provider.generate("System", "User")
            self.assertIn("Groq generation failed", str(ctx.exception))

    async def test_gemini_successful_response(self):
        with patch("google.genai.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_response = MagicMock()
            mock_response.text = "Ayushman Bharat coverage from Gemini."

            mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

            provider = GeminiProvider(api_key="gemini_mock_key", model="gemini-2.5-flash")
            answer = await provider.generate("System prompt", "User query")

            self.assertEqual(answer, "Ayushman Bharat coverage from Gemini.")
            mock_client.aio.models.generate_content.assert_called_once()

    async def test_gemini_error_handling(self):
        with patch("google.genai.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API quota depleted"))

            provider = GeminiProvider(api_key="gemini_mock_key")
            with self.assertRaises(RuntimeError) as ctx:
                await provider.generate("System", "User")
            self.assertIn("Gemini generation failed", str(ctx.exception))

    async def test_openai_successful_response(self):
        with patch("openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = "PMAY subsidy from OpenAI."
            mock_response.choices = [mock_choice]

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            provider = OpenAIProvider(api_key="sk-mock-key", model="gpt-4o-mini")
            answer = await provider.generate("System", "User")

            self.assertEqual(answer, "PMAY subsidy from OpenAI.")
            mock_client.chat.completions.create.assert_called_once()

    async def test_openai_error_handling(self):
        with patch("openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("Connection reset"))

            provider = OpenAIProvider(api_key="sk-mock-key")
            with self.assertRaises(RuntimeError) as ctx:
                await provider.generate("System", "User")
            self.assertIn("OpenAI generation failed", str(ctx.exception))


class TestLLMServiceAndGrounding(unittest.IsolatedAsyncioTestCase):
    """Tests for prompt templates, grounding constraints, and context construction."""

    def test_format_sources_context_empty(self):
        res = format_sources_context([])
        self.assertEqual(res, "No relevant scheme context available.")

    def test_format_sources_context_with_items(self):
        s1 = SourceItem(title="PM-KISAN", url="https://pmkisan.gov.in/", snippet="Provides ₹6,000 per year.")
        s2 = ProcessedChunk(
            chunk_id="pmay#0",
            scheme_id="pmay",
            title="PMAY-U",
            url="https://pmaymis.gov.in/",
            source_name="MoHUA",
            language="en",
            chunk_index=0,
            total_chunks=1,
            text="Provides financial subsidy for pucca houses.",
            char_length=42,
            metadata={},
        )

        formatted = format_sources_context([s1, s2])
        self.assertIn("[Source 1] Scheme: PM-KISAN", formatted)
        self.assertIn("Official URL: https://pmkisan.gov.in/", formatted)
        self.assertIn("Provides ₹6,000 per year.", formatted)
        self.assertIn("[Source 2] Scheme: PMAY-U", formatted)
        self.assertIn("Provides financial subsidy for pucca houses.", formatted)

    async def test_generate_answer_with_empty_sources(self):
        service = LLMService(provider=MockTestProvider())
        answer = await service.generate_answer("How to apply?", sources=[])
        self.assertIn("no matching scheme details were found", answer)

    async def test_generate_answer_grounding_prompt_structure(self):
        mock_provider = MockTestProvider("Factual grounded response.")
        service = LLMService(provider=mock_provider)

        s = SourceItem(title="PM-KISAN", url="https://pmkisan.gov.in/", snippet="Eligible farmers receive Rs 6,000.")
        answer = await service.generate_answer(query="What is the benefit?", sources=[s])

        self.assertEqual(answer, "Factual grounded response.")
        self.assertIsNotNone(mock_provider.last_system_prompt)
        self.assertIn("Strict Grounding", mock_provider.last_system_prompt)
        self.assertIn("Zero Hallucination", mock_provider.last_system_prompt)
        self.assertIn("No External Assumptions", mock_provider.last_system_prompt)
        self.assertIn("Handling Missing Data", mock_provider.last_system_prompt)

        self.assertIn("Citizen Question: What is the benefit?", mock_provider.last_user_prompt)
        self.assertIn("Scheme Context:", mock_provider.last_user_prompt)
        self.assertIn("PM-KISAN", mock_provider.last_user_prompt)

    async def test_empty_query_raises_error(self):
        service = LLMService(provider=MockTestProvider())
        with self.assertRaises(ValueError):
            await service.generate_answer(query="", sources=[])
        with self.assertRaises(ValueError):
            await service.generate_answer(query="   ", sources=[])


if __name__ == "__main__":
    unittest.main()
