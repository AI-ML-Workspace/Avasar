import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from app.models.document import ProcessedChunk, SchemeDocument
from app.services.chunking import chunk_document
from app.services.corpus_builder import CorpusBuilderService, CorpusSummary
from app.services.embedding import EmbeddingService
from app.services.rag import RAGService
from app.services.vector_store import FAISSVectorStore


class TestCorpusBuilder(unittest.TestCase):
    """Unit tests for the Unified Canonical Corpus Builder and FAISS Vector Indexing."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.raw_dir = Path(self.test_dir) / "raw"
        self.ingested_dir = Path(self.test_dir) / "ingested"
        self.processed_dir = Path(self.test_dir) / "processed"
        self.vector_dir = Path(self.test_dir) / "vector_store"

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.ingested_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        # Create sample curated scheme in raw_dir
        self.sample_curated = {
            "scheme_name": "Atal Pension Yojana (APY)",
            "description": "Atal Pension Yojana is a pension scheme for unorganized sector workers.",
            "eligibility": "Indian citizens aged 18 to 40 years with a bank account.",
            "benefits": ["Monthly pension ranging from Rs. 1000 to Rs. 5000 from age 60."],
            "official_source_url": "https://www.npscra.nsdl.co.in",
            "provider": "Pension Fund Regulatory and Development Authority (PFRDA)",
        }
        with open(self.raw_dir / "atal_pension_yojana.json", "w", encoding="utf-8") as f:
            json.dump(self.sample_curated, f, indent=2)

        # Create sample official-ingested source in ingested_dir
        pm_kisan_ingested = self.ingested_dir / "pm_kisan"
        pm_kisan_ingested.mkdir(parents=True, exist_ok=True)
        self.sample_official_doc = SchemeDocument(
            id="pm_kisan_portal_overview",
            title="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) Official Portal",
            url="https://pmkisan.gov.in/",
            source_id="pm_kisan",
            source_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            official_source_url="https://pmkisan.gov.in",
            source_type="scheme_portal",
            trust_level="primary_authoritative",
            retrieved_at="2026-09-05T00:00:00Z",
            published_at=None,
            content_hash="abc123pmkisanhash",
            document_type="portal_guideline",
            version=1,
            language="en",
            content="PM-Kisan is a Central Sector scheme with 100% funding from Government of India. Under the scheme an income support of 6,000 per year is provided in three equal installments. eKYC is mandatory for all registered farmers.",
            metadata={"ministry": "Ministry of Agriculture and Farmers Welfare"},
        )
        with open(pm_kisan_ingested / "schemes.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.sample_official_doc.model_dump(), ensure_ascii=False) + "\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # 1. Canonical Corpus Construction
    def test_canonical_corpus_construction(self):
        """Builder creates canonical documents.jsonl, chunks.jsonl, and corpus_manifest.json."""
        builder = CorpusBuilderService(chunk_size=500, chunk_overlap=100)
        summary = builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
        )

        self.assertEqual(summary.curated_documents, 1)
        self.assertEqual(summary.official_documents, 1)
        self.assertEqual(summary.total_documents, 2)
        self.assertGreater(summary.total_chunks, 0)
        self.assertEqual(summary.duplicates_removed, 0)

        docs_file = self.processed_dir / "documents.jsonl"
        chunks_file = self.processed_dir / "chunks.jsonl"
        manifest_file = self.processed_dir / "corpus_manifest.json"

        self.assertTrue(docs_file.exists())
        self.assertTrue(chunks_file.exists())
        self.assertTrue(manifest_file.exists())

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        self.assertEqual(manifest_data["total_documents"], 2)
        self.assertEqual(manifest_data["total_chunks"], summary.total_chunks)

    # 2. Merging Curated + Ingested Data
    def test_merging_curated_plus_ingested_preserves_both(self):
        """Curated knowledge and official ingested knowledge coexist additively."""
        builder = CorpusBuilderService()
        summary = builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
        )

        with open(self.processed_dir / "documents.jsonl", "r", encoding="utf-8") as f:
            docs = [json.loads(line) for line in f]

        doc_ids = {d["id"] for d in docs}
        self.assertIn("pm_kisan_portal_overview", doc_ids)
        self.assertTrue(any("atal_pension_yojana" in did for did in doc_ids))

    # 3. Deterministic Deduplication
    def test_deduplication_exact_content_hash(self):
        """Documents with identical content hashes are deduplicated."""
        builder = CorpusBuilderService()
        doc1 = SchemeDocument(
            id="doc_1",
            title="Doc One",
            content="Identical body text for deduplication test.",
            content_hash="identical_hash_123",
        )
        doc2 = SchemeDocument(
            id="doc_2",
            title="Doc Two",
            content="Identical body text for deduplication test.",
            content_hash="identical_hash_123",
        )

        merged, dupes = builder.deduplicate_and_merge([doc1], [doc2])
        self.assertEqual(len(merged), 1)
        self.assertEqual(dupes, 1)
        self.assertEqual(merged[0].id, "doc_1")

    def test_deduplication_version_update(self):
        """Higher-version official document supersedes older document with identical ID."""
        builder = CorpusBuilderService()
        old_doc = SchemeDocument(
            id="scheme_update_test",
            title="Scheme V1",
            content="Old content V1",
            version=1,
            content_hash="hash_v1",
        )
        new_doc = SchemeDocument(
            id="scheme_update_test",
            title="Scheme V2",
            content="New content V2",
            version=2,
            retrieved_at="2026-09-05T01:00:00Z",
            content_hash="hash_v2",
        )

        merged, dupes = builder.deduplicate_and_merge([old_doc], [new_doc])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].version, 2)
        self.assertEqual(merged[0].content, "New content V2")

    # 4. Provenance Preservation
    def test_provenance_preservation_across_chunks(self):
        """Chunks carry all required provenance fields."""
        builder = CorpusBuilderService()
        builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
        )

        with open(self.processed_dir / "chunks.jsonl", "r", encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f]

        pmkisan_chunks = [c for c in chunks if c.get("source_id") == "pm_kisan"]
        self.assertGreater(len(pmkisan_chunks), 0)

        chunk = pmkisan_chunks[0]
        self.assertEqual(chunk["source_id"], "pm_kisan")
        self.assertEqual(chunk["official_source_url"], "https://pmkisan.gov.in")
        self.assertEqual(chunk["source_type"], "scheme_portal")
        self.assertEqual(chunk["trust_level"], "primary_authoritative")
        self.assertEqual(chunk["document_type"], "portal_guideline")
        self.assertEqual(chunk["content_hash"], "abc123pmkisanhash")
        self.assertIn("eKYC is mandatory", chunk["text"])

    # 5. Repeated Corpus Builds (Idempotency)
    def test_repeated_corpus_builds_idempotent(self):
        """Running build_corpus twice on identical input produces identical counts and outputs."""
        builder = CorpusBuilderService()

        summary1 = builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
        )
        with open(self.processed_dir / "chunks.jsonl", "r", encoding="utf-8") as f:
            content1 = f.read()

        summary2 = builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
        )
        with open(self.processed_dir / "chunks.jsonl", "r", encoding="utf-8") as f:
            content2 = f.read()

        self.assertEqual(summary1.total_documents, summary2.total_documents)
        self.assertEqual(summary1.total_chunks, summary2.total_chunks)
        self.assertEqual(summary1.duplicates_removed, summary2.duplicates_removed)
        self.assertEqual(content1, content2)

    # 6. Vector/Corpus Count Integrity
    def test_vector_corpus_count_integrity(self):
        """Strict validation that FAISS ntotal == len(chunks) == len(metadata)."""
        builder = CorpusBuilderService()
        summary = builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
        )

        with open(self.processed_dir / "chunks.jsonl", "r", encoding="utf-8") as f:
            chunks = [ProcessedChunk.model_validate_json(line) for line in f]

        dim = 16
        # Generate mock embeddings for each chunk
        np.random.seed(42)
        mock_vecs = np.random.randn(len(chunks), dim).astype(np.float32)
        # L2 normalize
        norms = np.linalg.norm(mock_vecs, axis=1, keepdims=True)
        mock_vecs = mock_vecs / norms

        store = FAISSVectorStore(dimension=dim)
        store.add_chunks(chunks=chunks, embeddings=mock_vecs)

        index_file = self.vector_dir / "test_index.faiss"
        store.save(index_file)

        loaded_store = FAISSVectorStore.load(index_file)
        self.assertEqual(loaded_store.index.ntotal, len(chunks))
        self.assertEqual(len(loaded_store.chunks), len(chunks))
        self.assertEqual(loaded_store.index.ntotal, summary.total_chunks)

    # 7. Vector Metadata Alignment
    def test_vector_metadata_alignment(self):
        """Vector index N maps 1:1 to chunk N in metadata."""
        chunks = [
            ProcessedChunk(
                chunk_id=f"c_{i}",
                scheme_id=f"s_{i}",
                title=f"Title {i}",
                text=f"Text for chunk {i}",
                char_length=15,
                chunk_index=i,
                total_chunks=3,
            )
            for i in range(3)
        ]
        dim = 8
        np.random.seed(123)
        vecs = np.random.randn(3, dim).astype(np.float32)
        vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

        store = FAISSVectorStore(dimension=dim)
        store.add_chunks(chunks=chunks, embeddings=vecs)

        for i in range(3):
            self.assertEqual(store.chunks[i].chunk_id, f"c_{i}")
            self.assertEqual(store.chunks[i].title, f"Title {i}")

    # 8. Retrieval from Newly Ingested Content & 9. Existing Corpus Regression
    def test_retrieval_finds_official_ingested_and_curated(self):
        """RAGService retrieves both official PM-KISAN chunk and curated APY chunk."""
        chunks = [
            ProcessedChunk(
                chunk_id="curated_apy#0",
                scheme_id="atal_pension_yojana",
                title="Atal Pension Yojana (APY)",
                url="https://www.npscra.nsdl.co.in",
                source_name="PFRDA",
                text="Atal Pension Yojana provides guaranteed pension for unorganized sector.",
                char_length=65,
                chunk_index=0,
                total_chunks=1,
            ),
            ProcessedChunk(
                chunk_id="pm_kisan_portal_overview#0",
                scheme_id="pm_kisan_portal_overview",
                title="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) Official Portal",
                url="https://pmkisan.gov.in/",
                source_id="pm_kisan",
                official_source_url="https://pmkisan.gov.in",
                text="PM-KISAN eKYC is mandatory for all registered farmers to receive installments.",
                char_length=75,
                chunk_index=0,
                total_chunks=1,
            ),
        ]
        dim = 4
        # Create distinct orthogonal vectors
        vecs = np.array([
            [1.0, 0.0, 0.0, 0.0],  # APY vector
            [0.0, 1.0, 0.0, 0.0],  # PM-KISAN vector
        ], dtype=np.float32)

        store = FAISSVectorStore(dimension=dim)
        store.add_chunks(chunks, vecs)

        mock_emb = MagicMock(spec=EmbeddingService)
        # Mock embed_text to return query vectors matching either APY or PM-KISAN
        def mock_embed(text):
            if "ekyc" in text.lower() or "kisan" in text.lower():
                return np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
            return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

        mock_emb.embed_text.side_effect = mock_embed
        rag = RAGService(vector_store=store, embedding_service=mock_emb)

        # Query 1: PM-KISAN eKYC
        kisan_results = rag.retrieve_chunks("What are the PM-KISAN eKYC requirements?", top_k=1)
        self.assertEqual(len(kisan_results), 1)
        top_kisan, score_kisan = kisan_results[0]
        self.assertEqual(top_kisan.source_id, "pm_kisan")
        self.assertEqual(top_kisan.official_source_url, "https://pmkisan.gov.in")
        self.assertAlmostEqual(score_kisan, 1.0, places=4)

        # Query 2: Atal Pension Yojana
        apy_results = rag.retrieve_chunks("How does Atal Pension Yojana work?", top_k=1)
        self.assertEqual(len(apy_results), 1)
        top_apy, score_apy = apy_results[0]
        self.assertEqual(top_apy.scheme_id, "atal_pension_yojana")
        self.assertAlmostEqual(score_apy, 1.0, places=4)

    # 10. CLI Behavior
    def test_cli_build_corpus_dry_run(self):
        """CLI executes with --dry-run and prints formatted summary without writing files."""
        import sys
        cmd = [
            sys.executable,
            "scripts/build_corpus.py",
            "--dry-run",
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(Path(__file__).resolve().parents[2]),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Corpus Build Summary", proc.stdout)
        self.assertIn("Curated documents:", proc.stdout)
        self.assertIn("Official-source documents:", proc.stdout)
        self.assertIn("Total documents:", proc.stdout)
        self.assertIn("Total chunks:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
