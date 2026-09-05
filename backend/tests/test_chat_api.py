import unittest
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.api.chat import (
    get_language_pipeline,
    get_llm_service,
    get_rag_service,
)
from app.main import app
from app.models.chat import SourceItem
from app.services.language_pipeline import ProcessedQuery


class TestChatAPI(unittest.TestCase):
    """Integration and route tests for POST /api/chat with mocked services."""

    def setUp(self):
        self.client = TestClient(app)

        # Mock sample sources returned by RAG
        self.sample_sources = [
            SourceItem(
                title="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                url="https://pmkisan.gov.in/",
                snippet="Provides financial assistance of Rs. 6000 per year.",
                score=0.885,
            ),
            SourceItem(
                title="PM-KISAN Eligibility Criteria",
                url="https://pmkisan.gov.in/exclusions",
                snippet="All landholding farmer families are eligible.",
                score=0.812,
            ),
        ]

        # Create mock service instances
        self.mock_rag = MagicMock()
        self.mock_rag.retrieve = AsyncMock(return_value=self.sample_sources)

        self.mock_llm = MagicMock()
        self.mock_llm.generate_answer = AsyncMock(
            return_value="Under PM-KISAN, eligible farmers receive Rs 6,000 annually."
        )

        self.mock_pipeline = MagicMock()
        # Default behavior: English pass-through
        self.mock_pipeline.process_query = AsyncMock(
            return_value=ProcessedQuery(
                original_text="How much financial benefit is given under PM-KISAN?",
                detected_language="en",
                normalized_query="How much financial benefit is given under PM-KISAN?",
            )
        )
        self.mock_pipeline.translate_response = AsyncMock(
            side_effect=lambda answer, target_language: answer
        )

        # Apply FastAPI dependency overrides
        app.dependency_overrides[get_rag_service] = lambda: self.mock_rag
        app.dependency_overrides[get_llm_service] = lambda: self.mock_llm
        app.dependency_overrides[get_language_pipeline] = lambda: self.mock_pipeline

    def tearDown(self):
        # Clear dependency overrides
        app.dependency_overrides.clear()

    def test_english_request_end_to_end(self):
        payload = {
            "message": "How much financial benefit is given under PM-KISAN?",
            "conversation_id": "conv_eng_123",
        }
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIn("answer", data)
        self.assertEqual(data["language"], "en")
        self.assertEqual(data["conversation_id"], "conv_eng_123")
        self.assertEqual(len(data["sources"]), 2)
        self.assertEqual(data["sources"][0]["title"], "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)")
        self.assertEqual(data["sources"][0]["url"], "https://pmkisan.gov.in/")
        self.assertEqual(data["sources"][0]["score"], 0.885)

        # Confirm services were invoked with expected arguments
        self.mock_pipeline.process_query.assert_called_once()
        # RAG receives the expansion-enriched query for short scheme queries
        self.mock_rag.retrieve.assert_called_once_with(
            query="How much financial benefit is given under PM-KISAN? Pradhan Mantri Kisan Samman Nidhi farmer income support"
        )
        self.mock_llm.generate_answer.assert_called_once()

    def test_hindi_request_with_auto_detection_and_localization(self):
        hindi_text = "पीएम किसान में कितने पैसे मिलते हैं?"
        # Mock pipeline detecting Hindi and translating query to English
        self.mock_pipeline.process_query = AsyncMock(
            return_value=ProcessedQuery(
                original_text=hindi_text,
                detected_language="hi",
                normalized_query="How much money is received in PM Kisan?",
            )
        )
        self.mock_pipeline.translate_response = AsyncMock(
            return_value="पीएम किसान योजना के तहत पात्र किसानों को सालाना 6,000 रुपये मिलते हैं।"
        )

        payload = {
            "message": hindi_text,
            "conversation_id": "conv_hin_456",
        }
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["language"], "hi")
        self.assertEqual(
            data["answer"],
            "पीएम किसान योजना के तहत पात्र किसानों को सालाना 6,000 रुपये मिलते हैं।",
        )
        self.assertEqual(data["conversation_id"], "conv_hin_456")
        self.assertEqual(len(data["sources"]), 2)

        # RAG should receive the normalized English query, expanded for PM-KISAN
        self.mock_rag.retrieve.assert_called_once_with(
            query="How much money is received in PM Kisan? Pradhan Mantri Kisan Samman Nidhi farmer income support"
        )
        # translate_response should be called with target_language='hi'
        self.mock_pipeline.translate_response.assert_called_once()

    def test_bengali_request_with_explicit_language(self):
        bengali_text = "প্রধানমন্ত্রী কিষাণ যোজনা কী?"
        self.mock_pipeline.process_query = AsyncMock(
            return_value=ProcessedQuery(
                original_text=bengali_text,
                detected_language="bn",
                normalized_query="What is PM Kisan scheme?",
            )
        )
        self.mock_pipeline.translate_response = AsyncMock(
            return_value="পিএম কিষাণ প্রকল্পের আওতায় কৃষকরা বছরে ৬,০০০ টাকা পান।"
        )

        payload = {
            "message": bengali_text,
            "language": "bn",
            "conversation_id": "conv_bn_789",
        }
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["language"], "bn")
        self.assertEqual(
            data["answer"],
            "পিএম কিষাণ প্রকল্পের আওতায় কৃষকরা বছরে ৬,০০০ টাকা পান।",
        )
        self.assertEqual(data["conversation_id"], "conv_bn_789")

    def test_conversation_id_passthrough_when_none(self):
        payload = {
            "message": "What is PM Kisan?",
        }
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)
        cid = resp.json()["conversation_id"]
        self.assertIsNotNone(cid)
        self.assertTrue(cid.startswith("conv_"))

    def test_rag_failure_handled_gracefully(self):
        # When RAG retrieval encounters an unexpected error, sources defaults to empty
        self.mock_rag.retrieve = AsyncMock(side_effect=Exception("Database retrieval error"))
        self.mock_llm.generate_answer = AsyncMock(
            return_value="Based on verified records, no matching details were found."
        )

        payload = {"message": "Any scheme query"}
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["sources"], [])
        self.assertEqual(
            data["answer"],
            "Based on verified records, no matching details were found.",
        )

    def test_llm_failure_returns_503_without_leaking_secrets(self):
        # If upstream LLM provider fails, returns clean 503 error
        self.mock_llm.generate_answer = AsyncMock(
            side_effect=Exception("Groq API key 'sk-internal-secret-123' quota exceeded")
        )

        payload = {"message": "What is PM Kisan?"}
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 503)

        data = resp.json()
        self.assertIn("detail", data)
        # Secret / internal exception message must NOT be exposed
        self.assertNotIn("sk-internal-secret-123", str(data))
        self.assertEqual(
            data["detail"],
            "Service temporarily unable to generate an answer. Please try again later.",
        )

    def test_translation_failure_falls_back_to_english(self):
        # If outbound translation fails, fallback gracefully to English answer
        self.mock_pipeline.process_query = AsyncMock(
            return_value=ProcessedQuery(
                original_text="पीएम किसान योजना",
                detected_language="hi",
                normalized_query="PM Kisan Yojana",
            )
        )
        self.mock_pipeline.translate_response = AsyncMock(
            side_effect=Exception("Translation service unreachable")
        )

        payload = {"message": "पीएम किसान योजना"}
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        # Falls back to the English answer from LLM
        self.assertEqual(
            data["answer"],
            "Under PM-KISAN, eligible farmers receive Rs 6,000 annually.",
        )
        self.assertEqual(data["language"], "hi")

    def test_validation_error_empty_message(self):
        resp = self.client.post("/api/chat", json={"message": ""})
        self.assertEqual(resp.status_code, 422)

    def test_health_check(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok", "service": "avasar-api"})


if __name__ == "__main__":
    unittest.main()
