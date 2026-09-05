import json
import tempfile
import unittest
from pathlib import Path
import faiss
import numpy as np

from app.models.document import ProcessedChunk
from app.services.vector_store import FAISSVectorStore
from app.services.rag import RAGService


def _create_sample_chunk(chunk_id: str, title: str, text: str) -> ProcessedChunk:
    """Helper to generate a valid ProcessedChunk for testing."""
    return ProcessedChunk(
        chunk_id=chunk_id,
        scheme_id=chunk_id.split("#")[0],
        title=title,
        url=f"https://gov.in/{chunk_id}",
        source_name="Gov of India",
        language="en",
        chunk_index=0,
        total_chunks=1,
        text=text,
        char_length=len(text),
        metadata={"category": "Test"},
    )


class TestVectorStore(unittest.TestCase):
    """Isolated tests for FAISSVectorStore logic, persistence, and cosine similarity."""

    def setUp(self):
        self.dimension = 64
        self.store = FAISSVectorStore(dimension=self.dimension)

    def _generate_normalized_vector(self, seed: int = 42) -> np.ndarray:
        """Generate a deterministic unit-length vector of shape (dimension,)."""
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimension).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm

    def test_create_vector_store(self):
        self.assertEqual(self.store.dimension, 64)
        self.assertEqual(self.store.index.ntotal, 0)
        self.assertEqual(len(self.store.chunks), 0)

    def test_invalid_dimension_raises_error(self):
        with self.assertRaises(ValueError):
            FAISSVectorStore(dimension=0)
        with self.assertRaises(ValueError):
            FAISSVectorStore(dimension=-5)

    def test_add_chunks_success(self):
        v1 = self._generate_normalized_vector(1)
        v2 = self._generate_normalized_vector(2)
        embeddings = np.stack([v1, v2])

        c1 = _create_sample_chunk("scheme1#0", "PM Kisan", "Income support for farmers")
        c2 = _create_sample_chunk("scheme2#0", "PMAY", "Housing subsidy for citizens")

        self.store.add_chunks([c1, c2], embeddings)
        self.assertEqual(self.store.index.ntotal, 2)
        self.assertEqual(len(self.store.chunks), 2)
        self.assertEqual(self.store.chunks[0].title, "PM Kisan")
        self.assertEqual(self.store.chunks[1].title, "PMAY")

    def test_add_chunks_mismatch_raises_error(self):
        v1 = self._generate_normalized_vector(1)
        embeddings = np.stack([v1])  # 1 vector
        c1 = _create_sample_chunk("s1#0", "S1", "Text 1")
        c2 = _create_sample_chunk("s2#0", "S2", "Text 2")  # 2 chunks

        with self.assertRaises(ValueError):
            self.store.add_chunks([c1, c2], embeddings)

    def test_add_chunks_dimension_mismatch_raises_error(self):
        wrong_dim_embeddings = np.zeros((1, 32), dtype=np.float32)
        c1 = _create_sample_chunk("s1#0", "S1", "Text 1")

        with self.assertRaises(ValueError):
            self.store.add_chunks([c1], wrong_dim_embeddings)

    def test_similarity_search_and_ranking(self):
        v_target = self._generate_normalized_vector(10)
        v_other = self._generate_normalized_vector(99)
        embeddings = np.stack([v_target, v_other])

        c_target = _create_sample_chunk("target#0", "Target Scheme", "Relevant text")
        c_other = _create_sample_chunk("other#0", "Other Scheme", "Irrelevant text")

        self.store.add_chunks([c_target, c_other], embeddings)

        # Query identical to v_target should return target with score ~ 1.0
        results = self.store.search(v_target, top_k=2)
        self.assertEqual(len(results), 2)
        top_chunk, top_score = results[0]
        self.assertEqual(top_chunk.chunk_id, "target#0")
        self.assertAlmostEqual(top_score, 1.0, places=4)

    def test_top_k_behavior(self):
        vectors = [self._generate_normalized_vector(i) for i in range(5)]
        chunks = [_create_sample_chunk(f"s{i}#0", f"Scheme {i}", f"Text {i}") for i in range(5)]
        self.store.add_chunks(chunks, np.stack(vectors))

        # Ask for 2 results
        res_2 = self.store.search(vectors[0], top_k=2)
        self.assertEqual(len(res_2), 2)

        # Ask for more results than index size (5)
        res_10 = self.store.search(vectors[0], top_k=10)
        self.assertEqual(len(res_10), 5)

        # Invalid top_k
        with self.assertRaises(ValueError):
            self.store.search(vectors[0], top_k=0)
        with self.assertRaises(ValueError):
            self.store.search(vectors[0], top_k=-1)

    def test_save_and_load_integrity(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "test_index.faiss"

            v1 = self._generate_normalized_vector(1)
            v2 = self._generate_normalized_vector(2)
            c1 = _create_sample_chunk("c1#0", "Title 1", "Content 1")
            c2 = _create_sample_chunk("c2#0", "Title 2", "Content 2")

            self.store.add_chunks([c1, c2], np.stack([v1, v2]))
            self.store.save(index_path)

            self.assertTrue(index_path.exists())
            self.assertTrue(FAISSVectorStore._get_meta_path(index_path).exists())

            # Reload from disk
            loaded_store = FAISSVectorStore.load(index_path)
            self.assertEqual(loaded_store.dimension, self.dimension)
            self.assertEqual(loaded_store.index.ntotal, 2)
            self.assertEqual(len(loaded_store.chunks), 2)
            self.assertEqual(loaded_store.chunks[0].chunk_id, "c1#0")
            self.assertEqual(loaded_store.chunks[1].chunk_id, "c2#0")

            # Search on reloaded store gives identical result
            res = loaded_store.search(v1, top_k=1)
            self.assertEqual(res[0][0].chunk_id, "c1#0")
            self.assertAlmostEqual(res[0][1], 1.0, places=4)

    def test_load_missing_files_raise_error(self):
        with self.assertRaises(FileNotFoundError):
            FAISSVectorStore.load(Path("non_existent_path.faiss"))

    def test_load_corrupted_metadata_raises_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "bad.faiss"
            meta_path = FAISSVectorStore._get_meta_path(index_path)

            # Create an empty index file
            faiss.write_index(faiss.IndexFlatIP(self.dimension), str(index_path))

            # Write corrupted metadata (count mismatch)
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump({"dimension": self.dimension, "chunks": [{"title": "ghost"}]}, f)

            with self.assertRaises(ValueError):
                FAISSVectorStore.load(index_path)

    def test_search_lexical_fallback(self):
        c1 = _create_sample_chunk("s1#0", "INSPIRE Scholarship", "Financial aid and fellowship for science students")
        c2 = _create_sample_chunk("s2#0", "PM Kisan Samman Nidhi", "Income support for small and marginal landholder farmers")
        c3 = _create_sample_chunk("s3#0", "Ayushman Bharat PMJAY", "Health insurance cover for secondary and tertiary hospitalization")
        self.store.chunks = [c1, c2, c3]

        # Search for scholarship
        results = self.store.search_lexical("scholarship", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].title, "INSPIRE Scholarship")

        # Search for farmer
        results_farmer = self.store.search_lexical("farmer", top_k=2)
        self.assertGreater(len(results_farmer), 0)
        self.assertEqual(results_farmer[0][0].title, "PM Kisan Samman Nidhi")

        # Empty or whitespace query
        self.assertEqual(self.store.search_lexical(""), [])
        self.assertEqual(self.store.search_lexical("   "), [])

    def test_get_featured_chunks(self):
        c1 = _create_sample_chunk("s1#0", "PM Kisan", "Farmers support")
        c2 = _create_sample_chunk("s2#0", "Ayushman Bharat", "Healthcare")
        self.store.chunks = [c1, c2]

        featured = self.store.get_featured_chunks(top_k=2)
        self.assertEqual(len(featured), 2)
        titles = [c.title for c, _ in featured]
        self.assertIn("PM Kisan", titles)
        self.assertIn("Ayushman Bharat", titles)


class TestRAGServiceIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for RAGService connecting embeddings to FAISS retrieval."""

    class MockEmbeddingService:
        def __init__(self, dimension: int = 32):
            self.dimension = dimension

        def embed_text(self, text: str) -> np.ndarray:
            # Deterministic hash vector based on text
            rng = np.random.default_rng(abs(hash(text)) % (2**31))
            vec = rng.standard_normal(self.dimension).astype(np.float32)
            return vec / np.linalg.norm(vec)

    def setUp(self):
        self.dimension = 32
        self.mock_embedder = self.MockEmbeddingService(dimension=self.dimension)
        self.store = FAISSVectorStore(dimension=self.dimension)

        self.c1 = _create_sample_chunk("kisan#0", "PM Kisan", "Financial assistance to farmer families")
        self.c2 = _create_sample_chunk("pmay#0", "PMAY", "Affordable housing for urban poor")

        v1 = self.mock_embedder.embed_text(self.c1.text)
        v2 = self.mock_embedder.embed_text(self.c2.text)
        self.store.add_chunks([self.c1, self.c2], np.stack([v1, v2]))

        self.rag = RAGService(
            vector_store=self.store,
            embedding_service=self.mock_embedder,  # type: ignore
        )

    async def test_retrieve_returns_source_items(self):
        sources = await self.rag.retrieve("farmer assistance", top_k=2)
        self.assertEqual(len(sources), 2)
        self.assertIn(sources[0].title, [self.c1.title, self.c2.title])
        self.assertIsNotNone(sources[0].url)
        self.assertIsNotNone(sources[0].snippet)
        self.assertIsInstance(sources[0].score, float)

    def test_retrieve_chunks(self):
        results = self.rag.retrieve_chunks("farmer assistance", top_k=1)
        self.assertEqual(len(results), 1)
        chunk, score = results[0]
        self.assertIsInstance(chunk, ProcessedChunk)
        self.assertIsInstance(score, float)

    async def test_empty_query_raises_error(self):
        with self.assertRaises(ValueError):
            await self.rag.retrieve("", top_k=2)
        with self.assertRaises(ValueError):
            await self.rag.retrieve("   ", top_k=2)


class TestEmbeddingService(unittest.TestCase):
    """Tests for EmbeddingService error handling and inference contract."""

    def test_empty_input_raises_value_error(self):
        from app.services.embedding import EmbeddingService

        service = EmbeddingService(model_name="dummy")
        with self.assertRaises(ValueError):
            service.embed_text("")
        with self.assertRaises(ValueError):
            service.embed_text("   \n\t  ")
        with self.assertRaises(ValueError):
            service.embed_batch([])


if __name__ == "__main__":
    unittest.main()
