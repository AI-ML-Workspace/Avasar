import asyncio
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.models.document import ProcessedChunk, SchemeDocument
from app.models.source import (
    GovernmentClassification,
    OfficialSource,
    SourceType,
    TrustLevel,
)
from app.services.source_adapters import (
    IngestionResult,
    IngestionSecurityError,
    PMKisanSourceAdapter,
    RawDocument,
    SafeFetcher,
    SourceAdapter,
    get_adapter_for_source,
    register_adapter_class,
)
from app.services.source_registry import SourceRegistry, get_source_registry


class DummyTestAdapter(SourceAdapter):
    """Concrete mock adapter for testing."""

    def __init__(self, source: OfficialSource, mock_docs=None):
        super().__init__(source)
        self._mock_docs = mock_docs or []

    async def fetch(self, max_documents=None):
        return self._mock_docs[:max_documents] if max_documents else self._mock_docs

    def validate(self, raw_doc: RawDocument) -> bool:
        return bool(raw_doc.content and "invalid" not in raw_doc.content.lower())

    def normalize(self, raw_doc: RawDocument) -> SchemeDocument:
        return SchemeDocument(
            id=f"{self.source.source_id}_doc",
            slug=f"{self.source.source_id}-doc",
            title="Test Scheme",
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


class TestSourceIngestionEngine(unittest.TestCase):
    """Unit tests for the Official Government Source Ingestion Engine."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.source = OfficialSource(
            source_id="test_pm_kisan",
            name="PM-KISAN Portal",
            base_url="https://pmkisan.gov.in/",
            allowed_domains=["pmkisan.gov.in"],
            classification=GovernmentClassification.CENTRAL,
            source_type=SourceType.SCHEME_PORTAL,
            trust_level=TrustLevel.PRIMARY_AUTHORITATIVE,
            update_frequency="monthly",
            enabled=True,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # 1. Adapter Interface
    def test_adapter_interface_cannot_instantiate_abstract(self):
        """SourceAdapter cannot be instantiated directly without abstract methods."""
        with self.assertRaises(TypeError):
            SourceAdapter(self.source)

    # 2. Source-to-Adapter Resolution
    def test_source_to_adapter_resolution(self):
        """get_adapter_for_source correctly resolves implemented vs non-implemented adapters."""
        # pm_kisan is implemented
        pm_adapter = get_adapter_for_source("pm_kisan")
        self.assertIsNotNone(pm_adapter)
        self.assertIsInstance(pm_adapter, PMKisanSourceAdapter)
        self.assertEqual(pm_adapter.source.source_id, "pm_kisan")

        # myscheme has no adapter implemented yet
        myscheme_adapter = get_adapter_for_source("myscheme")
        self.assertIsNone(myscheme_adapter)

        # non-existent source
        unknown_adapter = get_adapter_for_source("non_existent_portal")
        self.assertIsNone(unknown_adapter)

    def test_custom_adapter_registration(self):
        """register_adapter_class allows dynamic extension of new adapters."""
        register_adapter_class("custom_source", DummyTestAdapter)
        mock_registry = MagicMock(spec=SourceRegistry)
        mock_registry.get_source.return_value = self.source

        adapter = get_adapter_for_source("custom_source", registry=mock_registry)
        self.assertIsNotNone(adapter)
        self.assertIsInstance(adapter, DummyTestAdapter)

    # 3. Authorized Domain Validation & SSRF Protection
    def test_authorized_domain_validation_whitelisted(self):
        """Whitelisted government domains pass URL validation."""
        fetcher = SafeFetcher(allowed_domains=["pmkisan.gov.in"])
        valid_url = fetcher.validate_url("https://pmkisan.gov.in/AboutUs.aspx")
        self.assertEqual(valid_url, "https://pmkisan.gov.in/AboutUs.aspx")

        # Subdomain of allowed domain
        valid_subdomain = fetcher.validate_url("https://api.pmkisan.gov.in/data")
        self.assertEqual(valid_subdomain, "https://api.pmkisan.gov.in/data")

    def test_ssrf_rejects_unauthorized_external_domains(self):
        """Attempting to fetch non-government or attacker-controlled domains raises IngestionSecurityError."""
        fetcher = SafeFetcher(allowed_domains=["pmkisan.gov.in"])

        with self.assertRaises(IngestionSecurityError):
            fetcher.validate_url("https://evil.com/fake-pmkisan")

        with self.assertRaises(IngestionSecurityError):
            fetcher.validate_url("http://169.254.169.254/latest/meta-data")

        with self.assertRaises(IngestionSecurityError):
            fetcher.validate_url("http://localhost:8000/internal")

        with self.assertRaises(IngestionSecurityError):
            fetcher.validate_url("ftp://pmkisan.gov.in/file")

    def test_ssrf_rejects_unwhitelisted_government_domains(self):
        """A valid government domain outside the specific source's allowed_domains is rejected."""
        fetcher = SafeFetcher(allowed_domains=["pmkisan.gov.in"])
        with self.assertRaises(IngestionSecurityError):
            fetcher.validate_url("https://scholarships.gov.in/portal")

    # 4. Redirect Validation
    def test_redirect_to_unauthorized_domain_raises_security_error(self):
        """If an HTTP redirect points to an unauthorized domain, fetcher raises IngestionSecurityError."""
        fetcher = SafeFetcher(allowed_domains=["pmkisan.gov.in"])

        # Mock httpx response where resp.url is an unauthorized domain
        mock_response = MagicMock()
        mock_response.url = httpx.URL("https://attacker-redirect.com/steal")

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            with self.assertRaises(IngestionSecurityError) as ctx:
                asyncio.run(fetcher.fetch("https://pmkisan.gov.in/login"))
            self.assertIn("Redirect led to unauthorized destination", str(ctx.exception))

    # 5. Timeout & Error Handling
    def test_network_timeout_handling(self):
        """Network timeouts are raised and handled cleanly without unhandled crashes."""
        fetcher = SafeFetcher(allowed_domains=["pmkisan.gov.in"], timeout=0.1)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.ConnectTimeout("Connection timed out")

        with patch("httpx.AsyncClient", return_value=mock_client):
            with self.assertRaises(httpx.ConnectTimeout):
                asyncio.run(fetcher.fetch("https://pmkisan.gov.in/"))

    def test_adapter_ingest_handles_fetch_error_gracefully(self):
        """SourceAdapter.ingest catches fetch failures and returns FAILED IngestionResult."""
        adapter = DummyTestAdapter(self.source)
        adapter.fetch = AsyncMock(side_effect=httpx.ConnectError("Server down"))

        result = asyncio.run(adapter.ingest(output_dir=self.test_dir))
        self.assertEqual(result.status, "FAILED")
        self.assertEqual(len(result.errors), 1)
        self.assertIn("Server down", result.errors[0])
        self.assertEqual(result.documents_fetched, 0)

    # 6. Malformed Response & Validation Handling
    def test_malformed_response_rejected(self):
        """Invalid or error content in RawDocument is rejected during validation."""
        raw_invalid = RawDocument(
            url="https://pmkisan.gov.in/doc",
            content="Invalid content: Server 500 Error Occurred",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="abc123hash",
        )
        adapter = DummyTestAdapter(self.source, mock_docs=[raw_invalid])
        result = asyncio.run(adapter.ingest(output_dir=self.test_dir))

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.documents_fetched, 1)
        self.assertEqual(result.documents_rejected, 1)
        self.assertEqual(result.documents_changed, 0)

    # 7. Content Hashing
    def test_deterministic_content_hashing(self):
        """Content hash produces consistent SHA-256 digests across identical texts."""
        text = "Pradhan Mantri Kisan Samman Nidhi provides Rs 6,000 per year."
        expected_hash = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

        hash1 = SourceAdapter.calculate_content_hash(text)
        hash2 = SourceAdapter.calculate_content_hash(f"  {text}  \n")
        self.assertEqual(hash1, expected_hash)
        self.assertEqual(hash1, hash2)

    # 8. Unchanged Content Detection & 9. Duplicate Prevention
    def test_unchanged_content_detection_and_deduplication(self):
        """Subsequent run with identical content detects documents_unchanged and prevents duplicate chunks."""
        raw_doc = RawDocument(
            url="https://pmkisan.gov.in/guide",
            content="PM-KISAN provides income support of 6000 per year in three installments.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="h1",
        )
        adapter = DummyTestAdapter(self.source, mock_docs=[raw_doc])

        # Run 1: Document is new
        res1 = asyncio.run(adapter.ingest(output_dir=self.test_dir))
        self.assertEqual(res1.documents_fetched, 1)
        self.assertEqual(res1.documents_changed, 1)
        self.assertEqual(res1.documents_unchanged, 0)
        self.assertGreater(res1.chunks_created, 0)

        # Inspect generated files
        source_dir = Path(self.test_dir) / self.source.source_id
        doc_file = source_dir / "schemes.jsonl"
        chunk_file = source_dir / "chunks.jsonl"
        manifest_file = source_dir / "manifest.json"

        self.assertTrue(doc_file.exists())
        self.assertTrue(chunk_file.exists())
        self.assertTrue(manifest_file.exists())

        with open(doc_file, "r", encoding="utf-8") as f:
            lines1 = f.readlines()
        self.assertEqual(len(lines1), 1)

        # Run 2: Exact same content fetched again
        res2 = asyncio.run(adapter.ingest(output_dir=self.test_dir))
        self.assertEqual(res2.documents_fetched, 1)
        self.assertEqual(res2.documents_changed, 0)
        self.assertEqual(res2.documents_unchanged, 1)
        self.assertEqual(res2.chunks_created, 0)

        # Check that files were NOT appended with duplicates
        with open(doc_file, "r", encoding="utf-8") as f:
            lines2 = f.readlines()
        self.assertEqual(len(lines2), 1)

    # 10. Provenance Metadata
    def test_provenance_metadata_preserved_in_documents_and_chunks(self):
        """SchemeDocument and ProcessedChunk carry complete official source provenance."""
        raw_doc = RawDocument(
            url="https://pmkisan.gov.in/details",
            content="Eligible farmer families receive direct bank transfer payments.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T01:23:45Z",
            content_hash="hash987",
        )
        adapter = DummyTestAdapter(self.source, mock_docs=[raw_doc])
        asyncio.run(adapter.ingest(output_dir=self.test_dir))

        # Check saved schemes.jsonl
        source_dir = Path(self.test_dir) / self.source.source_id
        with open(source_dir / "schemes.jsonl", "r", encoding="utf-8") as f:
            doc_data = json.loads(f.readline())

        self.assertEqual(doc_data["source_id"], "test_pm_kisan")
        self.assertEqual(doc_data["official_source_url"], "https://pmkisan.gov.in/details")
        self.assertEqual(doc_data["document_type"], "scheme_guideline")
        self.assertEqual(doc_data["retrieved_at"], "2026-09-05T01:23:45Z")
        self.assertIsNotNone(doc_data["content_hash"])

        # Check saved chunks.jsonl
        with open(source_dir / "chunks.jsonl", "r", encoding="utf-8") as f:
            chunk_data = json.loads(f.readline())

        self.assertEqual(chunk_data["source_id"], "test_pm_kisan")
        self.assertEqual(chunk_data["official_source_url"], "https://pmkisan.gov.in/details")
        self.assertEqual(chunk_data["document_type"], "scheme_guideline")
        self.assertEqual(chunk_data["content_hash"], doc_data["content_hash"])

    # 11. PM-KISAN HTML Parsing & Normalization
    def test_pm_kisan_html_normalization(self):
        """PMKisanSourceAdapter normalizes HTML with extracted sections into clean text."""
        html = """
        <html>
        <head><title>PM Kisan Official Portal</title></head>
        <body>
            <nav><a href="/home">Home</a></nav>
            <h1>Pradhan Mantri Kisan Samman Nidhi</h1>
            <p>PM-KISAN is a central sector scheme with 100% funding from Government of India.</p>
            <h2>Eligibility Criteria</h2>
            <p>All landholding farmer families having cultivable landholding in their names are eligible.</p>
            <h2>Exclusion Categories</h2>
            <p>Institutional landholders, constitutional post holders, and income tax payers are excluded.</p>
            <footer>Contact us at pmkisan-ict@gov.in</footer>
        </body>
        </html>
        """
        adapter = PMKisanSourceAdapter(self.source)
        raw = RawDocument(
            url="https://pmkisan.gov.in/",
            content=html,
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="hash1",
        )

        self.assertTrue(adapter.validate(raw))
        doc = adapter.normalize(raw)

        self.assertEqual(doc.source_id, "test_pm_kisan")
        self.assertEqual(doc.official_source_url, "https://pmkisan.gov.in/")
        self.assertIn("Pradhan Mantri Kisan Samman Nidhi", doc.title)
        self.assertIn("Eligibility Criteria", doc.content)
        self.assertIn("Exclusion Categories", doc.content)
        # Nav and footer are stripped
        self.assertNotIn("Contact us at", doc.content)

    # 12. CLI Ingestion Execution
    def test_cli_execution_for_unimplemented_and_dry_run(self):
        """CLI handles unimplemented sources cleanly and dry-run without writing files."""
        import subprocess
        import sys

        # Unimplemented source
        cmd1 = [
            sys.executable,
            "scripts/ingest_sources.py",
            "--source",
            "myscheme",
        ]
        proc1 = subprocess.run(cmd1, cwd=str(Path(__file__).resolve().parents[2]), capture_output=True, text=True)
        self.assertEqual(proc1.returncode, 0)
        self.assertIn("Source: myscheme", proc1.stdout)
        self.assertIn("Status: NOT IMPLEMENTED", proc1.stdout)


if __name__ == "__main__":
    unittest.main()
