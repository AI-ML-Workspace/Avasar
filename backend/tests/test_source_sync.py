import asyncio
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import numpy as np

from app.models.document import ProcessedChunk, SchemeDocument
from app.models.source import (
    GovernmentClassification,
    OfficialSource,
    SourceType,
    TrustLevel,
)
from app.services.source_adapters.base import (
    IngestionResult,
    RawDocument,
    SourceAdapter,
)
from app.services.source_registry import SourceRegistry
from app.services.source_sync import (
    SourceHealthRecord,
    SourceSyncReport,
    SourceSyncService,
)
from app.services.vector_store import FAISSVectorStore


class MockSyncAdapter(SourceAdapter):
    """Test adapter with configurable documents and behavior."""

    def __init__(self, source: OfficialSource, mock_docs=None, fetch_exception=None):
        super().__init__(source)
        self._mock_docs = mock_docs or []
        self._fetch_exception = fetch_exception

    async def fetch(self, max_documents=None):
        if self._fetch_exception:
            raise self._fetch_exception
        return self._mock_docs[:max_documents] if max_documents else self._mock_docs

    def validate(self, raw_doc: RawDocument) -> bool:
        return bool(raw_doc.content and "invalid" not in raw_doc.content)

    def normalize(self, raw_doc: RawDocument) -> SchemeDocument:
        return SchemeDocument(
            id=f"{self.source.source_id}_doc1",
            slug=f"{self.source.source_id}-doc1",
            title=f"Scheme from {self.source.source_id}",
            ministry="Test Ministry",
            summary="A test scheme summary.",
            content=raw_doc.content,
            source_url=raw_doc.url,
            official_source_url=raw_doc.url,
            source_id=self.source.source_id,
            retrieved_at=raw_doc.retrieved_at,
            content_hash=raw_doc.content_hash,
            document_type="scheme_guideline",
            tags=["test"],
        )


class TestSourceSync(unittest.TestCase):
    """Automated unit tests for Scheduled Official Source Synchronization (Phase 9)."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.raw_dir = self.test_dir / "raw"
        self.ingested_dir = self.test_dir / "ingested"
        self.processed_dir = self.test_dir / "processed"
        self.health_file = self.test_dir / "source_health.json"
        self.vector_store_path = self.test_dir / "vector_store" / "index.faiss"

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.ingested_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Create one minimal raw curated scheme file for corpus builder tests
        curated_doc = {
            "id": "curated_scheme_1",
            "slug": "curated-scheme-1",
            "title": "Curated National Scheme",
            "ministry": "Ministry of Finance",
            "summary": "Financial support for citizens.",
            "content": "Full guidelines for financial assistance under the curated national scheme.",
            "source_url": "https://finance.gov.in/scheme",
            "document_type": "scheme_guideline",
            "tags": ["finance"],
        }
        with open(self.raw_dir / "curated.json", "w", encoding="utf-8") as f:
            json.dump(curated_doc, f)

        # Mock source registry
        self.registry = SourceRegistry()
        self.src_a = OfficialSource(
            source_id="test_portal_a",
            name="Test Portal A",
            base_url="https://portal-a.gov.in/",
            allowed_domains=["portal-a.gov.in"],
            classification=GovernmentClassification.CENTRAL,
            source_type=SourceType.SCHEME_PORTAL,
            trust_level=TrustLevel.PRIMARY_AUTHORITATIVE,
        )
        self.src_b = OfficialSource(
            source_id="test_portal_b",
            name="Test Portal B",
            base_url="https://portal-b.gov.in/",
            allowed_domains=["portal-b.gov.in"],
            classification=GovernmentClassification.CENTRAL,
            source_type=SourceType.SCHEME_PORTAL,
            trust_level=TrustLevel.PRIMARY_AUTHORITATIVE,
        )
        self.registry.register_source(self.src_a)
        self.registry.register_source(self.src_b)

        self.sync_service = SourceSyncService(
            registry=self.registry,
            health_file=self.health_file,
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            processed_dir=self.processed_dir,
            vector_store_path=self.vector_store_path,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # 1. Mocked Source Success
    def test_mocked_source_success(self):
        """Test successful sync of an official source updates health and writes files."""
        raw_doc = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Valid official government policy content for Portal A.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Valid official government policy content for Portal A.").hexdigest(),
        )
        adapter = MockSyncAdapter(self.src_a, mock_docs=[raw_doc])

        health, result = asyncio.run(
            self.sync_service.sync_source(source_id="test_portal_a", adapter=adapter)
        )

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.documents_changed, 1)
        self.assertEqual(health.is_accessible, True)
        self.assertEqual(health.last_sync_status, "SUCCESS")
        self.assertEqual(health.last_http_status, 200)
        self.assertEqual(health.documents_total, 1)

        # Confirm persisted files exist
        doc_file = self.ingested_dir / "test_portal_a" / "schemes.jsonl"
        self.assertTrue(doc_file.exists())

    # 2. Timeout / Failure Handling
    def test_timeout_failure(self):
        """Test timeout or network failure records failed health without crashing."""
        exc = httpx.ConnectTimeout("Connection timed out to gateway portal")
        adapter = MockSyncAdapter(self.src_a, fetch_exception=exc)

        health, result = asyncio.run(
            self.sync_service.sync_source(source_id="test_portal_a", adapter=adapter)
        )

        self.assertEqual(result.status, "FAILED")
        self.assertEqual(health.is_accessible, False)
        self.assertEqual(health.last_sync_status, "FAILED")
        self.assertIn("Connection timed out", health.last_error)

    # 3. Unchanged Source Freshness Detection
    def test_unchanged_source_freshness(self):
        """Repeated sync of unchanged content skips rewriting and does not require rebuild."""
        raw_doc = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Identical content on both sync passes.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Identical content on both sync passes.").hexdigest(),
        )
        adapter = MockSyncAdapter(self.src_a, mock_docs=[raw_doc])

        # Run 1: initial ingestion
        asyncio.run(self.sync_service.sync_source("test_portal_a", adapter=adapter))

        # Run 2: same content
        health2, result2 = asyncio.run(self.sync_service.sync_source("test_portal_a", adapter=adapter))

        self.assertEqual(result2.status, "SUCCESS")
        self.assertEqual(result2.documents_changed, 0)
        self.assertEqual(result2.documents_unchanged, 1)
        self.assertEqual(health2.documents_changed, 0)
        self.assertEqual(health2.documents_unchanged, 1)
        self.assertEqual(health2.documents_total, 1)

    # 4. Changed Source Detection & Stale Invalidation
    def test_changed_source_detection(self):
        """Changed source content updates hash, replaces chunks, and triggers rebuild needed."""
        doc_v1 = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Version 1: Old guideline text.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Version 1: Old guideline text.").hexdigest(),
        )
        adapter_v1 = MockSyncAdapter(self.src_a, mock_docs=[doc_v1])
        asyncio.run(self.sync_service.sync_source("test_portal_a", adapter=adapter_v1))

        # Second sync with new content
        doc_v2 = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Version 2: Updated policy benefits and eligibility.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T01:00:00Z",
            content_hash=hashlib.sha256(b"Version 2: Updated policy benefits and eligibility.").hexdigest(),
        )
        adapter_v2 = MockSyncAdapter(self.src_a, mock_docs=[doc_v2])
        health2, result2 = asyncio.run(self.sync_service.sync_source("test_portal_a", adapter=adapter_v2))

        self.assertEqual(result2.documents_changed, 1)
        self.assertEqual(result2.documents_unchanged, 0)

        # Verify schemes.jsonl contains version 2 content
        doc_file = self.ingested_dir / "test_portal_a" / "schemes.jsonl"
        with open(doc_file, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("Version 2", lines[0]["content"])

    # 5. Partial Source Failure Isolation
    def test_partial_source_failure_isolation(self):
        """Failure of Portal A does not disrupt or prevent successful sync of Portal B."""
        doc_b = RawDocument(
            url="https://portal-b.gov.in/scheme",
            content="Portal B content is active and accessible.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Portal B content is active and accessible.").hexdigest(),
        )
        adapter_b = MockSyncAdapter(self.src_b, mock_docs=[doc_b])

        # Patch get_adapter_for_source so Portal A fails and Portal B succeeds
        def mock_get_adapter(source_id, registry=None):
            if source_id == "test_portal_a":
                return MockSyncAdapter(self.src_a, fetch_exception=httpx.HTTPStatusError("500 Error", request=None, response=MagicMock(status_code=500)))
            return adapter_b

        with patch("app.services.source_sync.get_adapter_for_source", side_effect=mock_get_adapter), \
             patch.object(self.sync_service, "rebuild_corpus_and_index") as mock_rebuild:
            report = asyncio.run(
                self.sync_service.sync_all(source_ids=["test_portal_a", "test_portal_b"], force_rebuild=False)
            )

        self.assertEqual(report.sources_attempted, 2)
        self.assertEqual(report.sources_failed, 1)
        self.assertEqual(report.sources_succeeded, 1)

        self.assertEqual(report.sources["test_portal_a"].is_accessible, False)
        self.assertEqual(report.sources["test_portal_a"].last_sync_status, "FAILED")

        self.assertEqual(report.sources["test_portal_b"].is_accessible, True)
        self.assertEqual(report.sources["test_portal_b"].last_sync_status, "SUCCESS")

    # 6. No Stale-Data Deletion on Temporary Failure
    def test_no_stale_data_deletion_on_temporary_failure(self):
        """Pre-existing good data is preserved intact when a subsequent sync attempt fails."""
        # Initial successful sync
        doc = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Good pre-existing official content.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Good pre-existing official content.").hexdigest(),
        )
        adapter = MockSyncAdapter(self.src_a, mock_docs=[doc])
        asyncio.run(self.sync_service.sync_source("test_portal_a", adapter=adapter))

        doc_file = self.ingested_dir / "test_portal_a" / "schemes.jsonl"
        self.assertTrue(doc_file.exists())
        initial_mtime = doc_file.stat().st_mtime_ns

        # Subsequent sync encounters 503 gateway outage
        failing_adapter = MockSyncAdapter(
            self.src_a,
            fetch_exception=httpx.HTTPStatusError("503 Gateway Down", request=None, response=MagicMock(status_code=503)),
        )
        health_fail, result_fail = asyncio.run(
            self.sync_service.sync_source("test_portal_a", adapter=failing_adapter)
        )

        self.assertEqual(result_fail.status, "FAILED")
        self.assertTrue(doc_file.exists(), "Existing schemes.jsonl must NOT be deleted.")
        self.assertEqual(doc_file.stat().st_mtime_ns, initial_mtime, "File should remain untouched.")
        self.assertEqual(health_fail.documents_total, 1, "Persisted document count must be retained.")

    # 7. Corpus and Index Integrity
    def test_corpus_and_index_integrity(self):
        """Rebuild produces canonical corpus and FAISS vector index with strict 1:1 chunk alignment."""
        doc = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Official Scheme content for corpus building and FAISS indexing.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Official Scheme content for corpus building and FAISS indexing.").hexdigest(),
        )
        adapter = MockSyncAdapter(self.src_a, mock_docs=[doc])
        asyncio.run(self.sync_service.sync_source("test_portal_a", adapter=adapter))

        # Mock embedding service to avoid loading heavy 400MB model in quick unit test
        dim = 768
        mock_embedding_service = MagicMock()
        mock_embedding_service.dimension = dim
        mock_embedding_service.embed_batch.side_effect = lambda texts, batch_size=32: np.random.randn(len(texts), dim).astype(np.float32)

        with patch("app.services.source_sync.get_embedding_service", return_value=mock_embedding_service):
            self.sync_service.rebuild_corpus_and_index()

        self.assertTrue(self.vector_store_path.exists())
        loaded_store = FAISSVectorStore.load(self.vector_store_path)

        chunks_file = self.processed_dir / "chunks.jsonl"
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunk_count = sum(1 for line in f if line.strip())

        self.assertEqual(loaded_store.index.ntotal, chunk_count)
        self.assertGreater(chunk_count, 0)
        self.assertEqual(loaded_store.dimension, dim)

    # 8. Dry Run Mode
    def test_dry_run_mode(self):
        """Dry-run validates ingestion without modifying disk or writing files."""
        doc = RawDocument(
            url="https://portal-a.gov.in/scheme",
            content="Dry run content should not be written to disk.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash=hashlib.sha256(b"Dry run content should not be written to disk.").hexdigest(),
        )
        adapter = MockSyncAdapter(self.src_a, mock_docs=[doc])

        health, result = asyncio.run(
            self.sync_service.sync_source("test_portal_a", adapter=adapter, dry_run=True)
        )

        self.assertEqual(result.status, "SUCCESS")
        doc_file = self.ingested_dir / "test_portal_a" / "schemes.jsonl"
        self.assertFalse(doc_file.exists(), "Dry-run must not create schemes.jsonl on disk.")


if __name__ == "__main__":
    unittest.main()
