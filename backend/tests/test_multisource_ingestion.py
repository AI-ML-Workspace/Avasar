import asyncio
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np

from app.models.document import ProcessedChunk, SchemeDocument
from app.models.source import OfficialSource
from app.services.corpus_builder import CorpusBuilderService
from app.services.embedding import EmbeddingService
from app.services.rag import RAGService
from app.services.source_adapters import (
    NSPSourceAdapter,
    PMAYUrbanSourceAdapter,
    PMMudraSourceAdapter,
    PMKisanSourceAdapter,
    RawDocument,
    get_adapter_for_source,
)
from app.services.source_registry import get_source_registry
from app.services.vector_store import FAISSVectorStore


class TestMultiSourceIngestion(unittest.TestCase):
    """Automated unit tests for Multi-Source Official Government Ingestion (Phase 8)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.registry = get_source_registry()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # 1. Source Adapter Resolution
    def test_adapter_resolution_for_all_supported_sources(self):
        """All implemented official source adapters resolve correctly from the registry."""
        sources_to_adapters = {
            "pm_kisan": PMKisanSourceAdapter,
            "nsp": NSPSourceAdapter,
            "pmay_urban": PMAYUrbanSourceAdapter,
            "pm_mudra": PMMudraSourceAdapter,
        }
        for source_id, expected_cls in sources_to_adapters.items():
            adapter = get_adapter_for_source(source_id, registry=self.registry)
            self.assertIsNotNone(adapter, f"Adapter for '{source_id}' should resolve.")
            self.assertIsInstance(adapter, expected_cls)
            self.assertEqual(adapter.source.source_id, source_id)

        # Unimplemented sources return None
        self.assertIsNone(get_adapter_for_source("myscheme", registry=self.registry))
        self.assertIsNone(get_adapter_for_source("data_gov", registry=self.registry))

    # 2. NSP Adapter Fetch, Validate, Normalize
    def test_nsp_adapter_validation_and_normalization(self):
        """NSPSourceAdapter validates official content and preserves provenance."""
        source = self.registry.get_source("nsp")
        self.assertIsNotNone(source)
        adapter = NSPSourceAdapter(source)

        mock_html = """
        <html>
        <head><title>NSP</title></head>
        <body>
            <h1>National Scholarship Portal</h1>
            <p>The National Scholarship Portal is a common electronic portal for scholarships schemes for students.</p>
            <p>Direct Benefit Transfer (DBT) ensures funds reach student bank accounts directly.</p>
        </body>
        </html>
        """
        raw = RawDocument(
            url="https://scholarships.gov.in/aboutUs",
            content=mock_html,
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="nsp_hash_1",
        )
        self.assertTrue(adapter.validate(raw))
        doc = adapter.normalize(raw)

        self.assertEqual(doc.source_id, "nsp")
        self.assertEqual(doc.official_source_url, "https://scholarships.gov.in")
        self.assertEqual(doc.source_type, "ministry_portal")
        self.assertEqual(doc.trust_level, "primary_authoritative")
        self.assertIn("National Scholarship Portal", doc.title)
        self.assertIn("Direct Benefit Transfer", doc.content)

    # 3. PMAY-U Adapter Fetch, Validate, Normalize
    def test_pmay_urban_adapter_validation_and_normalization(self):
        """PMAYUrbanSourceAdapter normalizes CLSS and FAQ pages with full provenance."""
        source = self.registry.get_source("pmay_urban")
        self.assertIsNotNone(source)
        adapter = PMAYUrbanSourceAdapter(source)

        mock_clss_html = """
        <html>
        <head><title>PMAY-U CLSS</title></head>
        <body>
            <h1>Credit Linked Subsidy Scheme (CLSS)</h1>
            <p>PMAY Urban provides interest subsidy for housing loans for EWS, LIG and MIG categories.</p>
            <p>Interest subsidy of 6.5% is provided for EWS/LIG on loan amounts up to Rs. 6 lakh.</p>
        </body>
        </html>
        """
        raw = RawDocument(
            url="https://pmay-urban.gov.in/credit-linked-subsidy-scheme",
            content=mock_clss_html,
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="pmay_hash_1",
        )
        self.assertTrue(adapter.validate(raw))
        doc = adapter.normalize(raw)

        self.assertEqual(doc.source_id, "pmay_urban")
        self.assertEqual(doc.official_source_url, "https://pmay-urban.gov.in")
        self.assertIn("Credit Linked Subsidy Scheme", doc.title)
        self.assertIn("6.5%", doc.content)

    # 4. PM MUDRA Adapter Fetch, Validate, Normalize
    def test_pm_mudra_adapter_validation_and_normalization(self):
        """PMMudraSourceAdapter parses loan categories (Shishu, Kishor, Tarun) accurately."""
        source = self.registry.get_source("pm_mudra")
        self.assertIsNotNone(source)
        adapter = PMMudraSourceAdapter(source)

        mock_mudra_html = """
        <html>
        <head><title>MUDRA</title></head>
        <body>
            <h1>Pradhan Mantri MUDRA Yojana (PMMY)</h1>
            <p>MUDRA provides collateral-free loans up to Rs. 10 lakh to micro-enterprises.</p>
            <p>Loan products include Shishu (up to Rs. 50,000), Kishor (Rs. 50,000 to Rs. 5 lakh), and Tarun (Rs. 5 lakh to Rs. 10 lakh).</p>
            <p>Applications can be filed online on Udyamimitra portal.</p>
        </body>
        </html>
        """
        raw = RawDocument(
            url="https://www.mudra.org.in/",
            content=mock_mudra_html,
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="mudra_hash_1",
        )
        self.assertTrue(adapter.validate(raw))
        doc = adapter.normalize(raw)

        self.assertEqual(doc.source_id, "pm_mudra")
        self.assertEqual(doc.official_source_url, "https://www.mudra.org.in")
        self.assertIn("MUDRA", doc.title)
        self.assertIn("Shishu", doc.content)
        self.assertIn("Tarun", doc.content)

    # 5. Stale Content Replacement & Freshness
    def test_stale_content_replacement_on_content_change(self):
        """When source content changes, the older version is replaced without preserving stale content."""
        source = self.registry.get_source("pm_mudra")
        adapter = PMMudraSourceAdapter(source)

        raw_v1 = RawDocument(
            url="https://www.mudra.org.in/Home/PMMY",
            content="Pradhan Mantri MUDRA Yojana (PMMY) loans under MUDRA offer Shishu loans up to Rs 50,000 for micro enterprises and entrepreneurs.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T00:00:00Z",
            content_hash="hash_v1",
        )
        adapter.fetch = AsyncMock(return_value=[raw_v1])
        res1 = asyncio.run(adapter.ingest(output_dir=self.test_dir))
        self.assertEqual(res1.documents_changed, 1)

        source_dir = Path(self.test_dir) / "pm_mudra"
        with open(source_dir / "schemes.jsonl", "r", encoding="utf-8") as f:
            lines1 = f.readlines()
        self.assertEqual(len(lines1), 1)

        # Version 2: Content updated officially
        raw_v2 = RawDocument(
            url="https://www.mudra.org.in/Home/PMMY",
            content="Pradhan Mantri MUDRA Yojana (PMMY) loans under MUDRA offer TarunPlus loans up to Rs 20 Lakh for established micro enterprises.",
            content_type="text/html",
            status_code=200,
            retrieved_at="2026-09-05T01:00:00Z",
            content_hash="hash_v2",
        )
        adapter.fetch = AsyncMock(return_value=[raw_v2])
        res2 = asyncio.run(adapter.ingest(output_dir=self.test_dir))
        self.assertEqual(res2.documents_changed, 1)
        self.assertEqual(res2.documents_unchanged, 0)

        # Confirm schemes.jsonl still has exactly 1 entry and contains the fresh content
        with open(source_dir / "schemes.jsonl", "r", encoding="utf-8") as f:
            lines2 = f.readlines()
        self.assertEqual(len(lines2), 1)
        self.assertIn("TarunPlus", lines2[0])
        self.assertNotIn("hash_v1", lines2[0])

    # 6. Multi-Source Corpus Unification
    def test_multisource_corpus_unification(self):
        """CorpusBuilderService unifies curated and all 4 official sources additively."""
        raw_dir = Path(self.test_dir) / "raw"
        ingested_dir = Path(self.test_dir) / "ingested"
        processed_dir = Path(self.test_dir) / "processed"
        raw_dir.mkdir(parents=True, exist_ok=True)
        ingested_dir.mkdir(parents=True, exist_ok=True)

        # Curated scheme
        with open(raw_dir / "pmay_urban.json", "w", encoding="utf-8") as f:
            json.dump({
                "scheme_name": "Pradhan Mantri Awas Yojana (PMAY-U)",
                "description": "Housing scheme for urban poor.",
                "official_source_url": "https://pmay-urban.gov.in/",
            }, f)

        # Official sources
        for s_id in ["pm_kisan", "nsp", "pm_mudra"]:
            s_dir = ingested_dir / s_id
            s_dir.mkdir(parents=True, exist_ok=True)
            doc = SchemeDocument(
                id=f"{s_id}_overview",
                title=f"{s_id.upper()} Official Document",
                content=f"Authoritative official details for {s_id}.",
                source_id=s_id,
                official_source_url=f"https://{s_id}.gov.in",
            )
            with open(s_dir / "schemes.jsonl", "w", encoding="utf-8") as f:
                f.write(json.dumps(doc.model_dump()) + "\n")

        builder = CorpusBuilderService()
        summary = builder.build_corpus(
            raw_dir=raw_dir,
            ingested_dir=ingested_dir,
            output_dir=processed_dir,
        )
        self.assertEqual(summary.curated_documents, 1)
        self.assertEqual(summary.official_documents, 3)
        self.assertEqual(summary.total_documents, 4)
        self.assertIn("pm_kisan", summary.sources_represented)
        self.assertIn("nsp", summary.sources_represented)
        self.assertIn("pm_mudra", summary.sources_represented)

    # 7. Multi-Source Vector Search & 8. Unrelated Query Behavior
    def test_multisource_retrieval_and_unrelated_query(self):
        """RAGService retrieves appropriate source chunks across all official sources."""
        chunks = [
            ProcessedChunk(
                chunk_id="nsp#0",
                scheme_id="nsp_portal",
                title="National Scholarship Portal (NSP)",
                source_id="nsp",
                official_source_url="https://scholarships.gov.in",
                text="National Scholarship Portal enables direct scholarship disbursal to eligible students.",
                char_length=95,
                chunk_index=0,
                total_chunks=1,
            ),
            ProcessedChunk(
                chunk_id="pmay#0",
                scheme_id="pmay_urban_portal",
                title="PMAY Urban CLSS",
                source_id="pmay_urban",
                official_source_url="https://pmay-urban.gov.in",
                text="PMAY Urban Credit Linked Subsidy Scheme provides 6.5% interest subsidy for affordable housing.",
                char_length=99,
                chunk_index=0,
                total_chunks=1,
            ),
            ProcessedChunk(
                chunk_id="mudra#0",
                scheme_id="pm_mudra_portal",
                title="Pradhan Mantri MUDRA Yojana",
                source_id="pm_mudra",
                official_source_url="https://www.mudra.org.in",
                text="MUDRA offers Shishu loans up to 50,000, Kishor up to 5 lakh, and Tarun loans up to 10 lakh.",
                char_length=98,
                chunk_index=0,
                total_chunks=1,
            ),
        ]
        dim = 3
        # Orthogonal unit vectors for perfect simulated matching
        vecs = np.array([
            [1.0, 0.0, 0.0],  # NSP
            [0.0, 1.0, 0.0],  # PMAY
            [0.0, 0.0, 1.0],  # MUDRA
        ], dtype=np.float32)

        store = FAISSVectorStore(dimension=dim)
        store.add_chunks(chunks, vecs)

        mock_emb = MagicMock(spec=EmbeddingService)
        def mock_embed(text):
            t = text.lower()
            if "scholarship" in t or "student" in t:
                return np.array([1.0, 0.0, 0.0], dtype=np.float32)
            if "housing" in t or "pmay" in t or "subsidy" in t:
                return np.array([0.0, 1.0, 0.0], dtype=np.float32)
            if "mudra" in t or "shishu" in t or "loan" in t:
                return np.array([0.0, 0.0, 1.0], dtype=np.float32)
            # Unrelated query (nearly orthogonal to all)
            return np.array([0.1, 0.1, 0.1], dtype=np.float32) / np.sqrt(0.03)

        mock_emb.embed_text.side_effect = mock_embed
        rag = RAGService(vector_store=store, embedding_service=mock_emb)

        # 1. NSP Query
        nsp_res = rag.retrieve_chunks("scholarships for college students", top_k=1)
        self.assertEqual(nsp_res[0][0].source_id, "nsp")
        self.assertAlmostEqual(nsp_res[0][1], 1.0, places=3)

        # 2. PMAY Query
        pmay_res = rag.retrieve_chunks("affordable housing interest subsidy", top_k=1)
        self.assertEqual(pmay_res[0][0].source_id, "pmay_urban")
        self.assertAlmostEqual(pmay_res[0][1], 1.0, places=3)

        # 3. MUDRA Query
        mudra_res = rag.retrieve_chunks("Mudra loan for small business", top_k=1)
        self.assertEqual(mudra_res[0][0].source_id, "pm_mudra")
        self.assertAlmostEqual(mudra_res[0][1], 1.0, places=3)

        # 4. Unrelated Query
        cake_res = rag.retrieve_chunks("how to bake chocolate cookies", top_k=1)
        self.assertLess(cake_res[0][1], 0.6)

    # 9. FAISS Integrity Check
    def test_faiss_integrity_across_multisource_chunks(self):
        """Strict 1:1 integrity check across all multisource chunks."""
        chunks = [
            ProcessedChunk(
                chunk_id=f"c_{i}",
                scheme_id=f"s_{i}",
                title=f"Title {i}",
                text=f"Sample text chunk {i}",
                char_length=20,
                chunk_index=i,
                total_chunks=5,
            )
            for i in range(5)
        ]
        dim = 8
        np.random.seed(42)
        vecs = np.random.randn(5, dim).astype(np.float32)
        vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

        store = FAISSVectorStore(dimension=dim)
        store.add_chunks(chunks, vecs)

        idx_path = Path(self.test_dir) / "test.faiss"
        store.save(idx_path)
        loaded = FAISSVectorStore.load(idx_path)

        self.assertEqual(loaded.index.ntotal, 5)
        self.assertEqual(len(loaded.chunks), 5)
        self.assertEqual(loaded.dimension, 8)


if __name__ == "__main__":
    unittest.main()
