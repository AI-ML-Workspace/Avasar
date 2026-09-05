import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.chat import ChatRequest, ChatResponse, SourceItem
from app.models.document import ProcessedChunk
from app.models.source import (
    GovernmentClassification,
    OfficialSource,
    OfficialSourcePublic,
    SourceType,
    TrustLevel,
    is_authorized_government_domain,
)
from app.services.rag import RAGService
from app.services.source_registry import SourceRegistry


class TestCitationTrust(unittest.TestCase):
    """Unit and integration tests for Citation Transparency and Source Trust (Phase 10)."""

    def setUp(self):
        self.client = TestClient(app)
        self.registry = SourceRegistry()

    # 1. Source Metadata Mapping
    def test_source_metadata_mapping(self):
        """OfficialSource converts to safe OfficialSourcePublic metadata."""
        src = OfficialSource(
            source_id="nsp",
            name="National Scholarship Portal",
            base_url="https://scholarships.gov.in/",
            allowed_domains=["scholarships.gov.in"],
            classification=GovernmentClassification.CENTRAL,
            source_type=SourceType.SCHEME_PORTAL,
            trust_level=TrustLevel.PRIMARY_AUTHORITATIVE,
        )

        public_meta = src.to_public_metadata(
            last_synced_at="2026-09-05T01:00:00Z",
            sync_status="SUCCESS",
        )

        self.assertIsInstance(public_meta, OfficialSourcePublic)
        self.assertEqual(public_meta.source_id, "nsp")
        self.assertEqual(public_meta.name, "National Scholarship Portal")
        self.assertEqual(public_meta.official_domain, "scholarships.gov.in")
        self.assertEqual(public_meta.source_url, "https://scholarships.gov.in/")
        self.assertEqual(public_meta.trust_level, "primary_authoritative")
        self.assertEqual(public_meta.classification, "central")
        self.assertEqual(public_meta.sync_status, "success")
        self.assertEqual(public_meta.last_synced_at, "2026-09-05T01:00:00Z")
        self.assertTrue(public_meta.is_official)

    # 2. Trust Classification Rules
    def test_trust_classification_rules(self):
        """Verify strict government domain authorization rules."""
        # Official domains
        self.assertTrue(is_authorized_government_domain("pmkisan.gov.in"))
        self.assertTrue(is_authorized_government_domain("scholarships.gov.in"))
        self.assertTrue(is_authorized_government_domain("pmay-urban.gov.in"))
        self.assertTrue(is_authorized_government_domain("mudra.org.in"))
        self.assertTrue(is_authorized_government_domain("myscheme.gov.in"))
        self.assertTrue(is_authorized_government_domain("karnataka.gov.in"))

        # Unverified / third-party / commercial domains
        self.assertFalse(is_authorized_government_domain("example.com"))
        self.assertFalse(is_authorized_government_domain("pmkisan-fake-blog.com"))
        self.assertFalse(is_authorized_government_domain("scholarship-portal.org"))
        self.assertFalse(is_authorized_government_domain("gov.in.scam.site"))
        self.assertFalse(is_authorized_government_domain(""))

    # 3. No Secrets or Internal Paths Exposed
    def test_no_secrets_or_internal_paths_exposed(self):
        """Ensure public source metadata contains no internal filesystem paths or secret keys."""
        resp = self.client.get("/api/schemes/sources")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        forbidden_tokens = ["sk-", "key", "secret", "token", "password", "f:\\", "c:\\", "/users/", ".env"]
        raw_text = resp.text.lower()

        for token in forbidden_tokens:
            self.assertNotIn(
                token,
                raw_text,
                f"Forbidden sensitive token '{token}' found in public sources endpoint response!"
            )

    # 4. GET /api/schemes/sources Endpoint
    def test_get_schemes_sources_endpoint(self):
        """GET /api/schemes/sources returns valid list of official sources with health telemetry."""
        resp = self.client.get("/api/schemes/sources")
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIn("sources", data)
        self.assertIsInstance(data["sources"], list)
        self.assertGreaterEqual(len(data["sources"]), 4)

        source_map = {s["source_id"]: s for s in data["sources"]}
        self.assertIn("pm_kisan", source_map)
        self.assertIn("nsp", source_map)
        self.assertIn("pmay_urban", source_map)
        self.assertIn("pm_mudra", source_map)

        # Validate structure of an active source
        nsp_data = source_map["nsp"]
        self.assertEqual(nsp_data["source_id"], "nsp")
        self.assertEqual(nsp_data["official_domain"], "scholarships.gov.in")
        self.assertEqual(nsp_data["is_official"], True)
        self.assertIn(nsp_data["sync_status"], ["success", "unknown"])

    # 5. Missing Health Record Handling
    def test_missing_health_record_handling(self):
        """Registered source with no previous sync health record returns graceful unknown status."""
        mock_sync_service = MagicMock()
        mock_sync_service.load_health.return_value = {}  # No health records recorded

        from app.api.schemes import get_source_sync_service
        app.dependency_overrides[get_source_sync_service] = lambda: mock_sync_service
        try:
            resp = self.client.get("/api/schemes/sources")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()

            for src in data["sources"]:
                self.assertEqual(src["sync_status"], "unknown")
                self.assertIsNone(src["last_synced_at"])
        finally:
            app.dependency_overrides.clear()

    # 6. Unknown / Unregistered Source Handling in RAG
    def test_unknown_source_in_rag(self):
        """RAG marks unregistered non-government citations as unverified."""
        mock_chunk = ProcessedChunk(
            chunk_id="test#0",
            scheme_id="unregistered_scheme",
            title="Unregistered Blog Post",
            url="https://external-blog.com/article",
            text="Unverified information about government schemes.",
            chunk_index=0,
            total_chunks=1,
            char_length=48,
        )

        rag = RAGService(vector_store_path="dummy/path")
        with patch.object(rag, "retrieve_chunks", return_value=[(mock_chunk, 0.75)]):
            sources = asyncio_run(rag.retrieve("any query"))

        self.assertEqual(len(sources), 1)
        s = sources[0]
        self.assertEqual(s.title, "Unregistered Blog Post")
        self.assertEqual(s.url, "https://external-blog.com/article")
        self.assertFalse(s.is_official)
        self.assertEqual(s.trust_level, "unverified")
        self.assertIsNone(s.classification)
        self.assertEqual(s.official_domain, "external-blog.com")

    # 7. POST /api/chat Source Metadata Enrichment
    def test_api_chat_source_metadata_enrichment(self):
        """POST /api/chat includes enriched trust metadata in returned sources."""
        enriched_source = SourceItem(
            title="National Scholarship Portal (NSP)",
            url="https://scholarships.gov.in/",
            snippet="Official scholarship portal for pre-matric and post-matric schemes.",
            score=0.88,
            source_id="nsp",
            is_official=True,
            trust_level="primary_authoritative",
            classification="central",
            official_domain="scholarships.gov.in",
            last_synced_at="2026-09-05T00:53:04.144855+00:00",
        )

        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[enriched_source])

        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(
            return_value="Students can apply for scholarships via scholarships.gov.in."
        )

        from app.api.chat import get_rag_service, get_llm_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm

        try:
            resp = self.client.post("/api/chat", json={"message": "How do I apply for NSP scholarships?"})
            self.assertEqual(resp.status_code, 200)

            body = resp.json()
            self.assertIn("sources", body)
            self.assertEqual(len(body["sources"]), 1)

            src = body["sources"][0]
            self.assertEqual(src["title"], "National Scholarship Portal (NSP)")
            self.assertEqual(src["url"], "https://scholarships.gov.in/")
            self.assertEqual(src["source_id"], "nsp")
            self.assertEqual(src["is_official"], True)
            self.assertEqual(src["trust_level"], "primary_authoritative")
            self.assertEqual(src["classification"], "central")
            self.assertEqual(src["official_domain"], "scholarships.gov.in")
            self.assertIsNotNone(src["last_synced_at"])

        finally:
            app.dependency_overrides.clear()

    # 8. Backward Compatibility with Existing Chat Response Contract
    def test_chat_response_backward_compatibility(self):
        """ChatResponse maintains seamless compatibility with legacy 4-field source consumers."""
        # Deserialization with legacy fields only
        legacy_data = {
            "answer": "This is an answer.",
            "language": "en",
            "sources": [
                {
                    "title": "PM Kisan Portal",
                    "url": "https://pmkisan.gov.in/",
                    "snippet": "Income support scheme.",
                    "score": 0.85,
                }
            ],
            "conversation_id": "conv_123",
        }
        res = ChatResponse.model_validate(legacy_data)
        self.assertEqual(res.sources[0].title, "PM Kisan Portal")
        self.assertEqual(res.sources[0].score, 0.85)
        # Default official status should be True
        self.assertTrue(res.sources[0].is_official)


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
