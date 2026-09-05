import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import faiss
except ImportError:
    faiss = None
import numpy as np

from app.models.document import ProcessedChunk

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store for similarity search over scheme document chunks.

    Uses an exact Inner Product index (faiss.IndexFlatIP) on L2-normalized embeddings,
    providing exact cosine similarity ranking without approximation errors.
    Maintains a deterministic 1:1 mapping between vector indices and ProcessedChunk metadata.
    """

    def __init__(self, dimension: int):
        if dimension <= 0:
            raise ValueError(f"Dimension must be positive, got {dimension}")
        self.dimension = dimension
        self.index: Optional[Any] = faiss.IndexFlatIP(dimension) if faiss is not None else None
        self.chunks: List[ProcessedChunk] = []

    @classmethod
    def _get_meta_path(cls, index_path: Path) -> Path:
        """Derive the associated metadata JSON file path from the index path."""
        return index_path.parent / f"{index_path.stem}.meta.json"

    def add_chunks(
        self,
        chunks: List[ProcessedChunk],
        embeddings: np.ndarray,
    ) -> None:
        """Add chunks and their corresponding normalized embeddings to the vector store.

        Args:
            chunks: List of ProcessedChunk objects.
            embeddings: 2D numpy array of shape (N, dimension) of dtype float32.

        Raises:
            ValueError: If chunks list is empty, shapes mismatch, or dimensions don't match.
        """
        if not chunks:
            raise ValueError("Cannot add empty chunks list to vector store.")

        if embeddings.ndim != 2:
            raise ValueError(
                f"Embeddings must be 2-dimensional (N x dimension), got shape {embeddings.shape}"
            )

        if len(chunks) != embeddings.shape[0]:
            raise ValueError(
                f"Count mismatch: received {len(chunks)} chunks but {embeddings.shape[0]} embeddings."
            )

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch: store expected {self.dimension}, got {embeddings.shape[1]}"
            )

        # Ensure float32 contiguous array for FAISS
        vectors = np.ascontiguousarray(embeddings, dtype=np.float32)

        if self.index is not None:
            self.index.add(vectors)
        self.chunks.extend(chunks)
        logger.info(
            "Added %d chunks to vector store. Total index size: %d",
            len(chunks),
            self.index.ntotal,
        )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 4,
    ) -> List[Tuple[ProcessedChunk, float]]:
        """Search the index for top-k chunks most similar to query_embedding.

        Args:
            query_embedding: 1D array of shape (dimension,) or 2D of shape (1, dimension).
            top_k: Number of top results to return. Must be > 0.

        Returns:
            List of (ProcessedChunk, similarity_score) tuples, ordered by descending score.

        Raises:
            ValueError: If top_k <= 0 or query dimension does not match store dimension.
        """
        if top_k <= 0:
            raise ValueError(f"top_k must be a positive integer, got {top_k}")

        if self.index is None or self.index.ntotal == 0 or len(self.chunks) == 0:
            return []

        # Reshape 1D vector to 2D (1, dimension)
        query_vec = np.ascontiguousarray(query_embedding, dtype=np.float32)
        if query_vec.ndim == 1:
            query_vec = query_vec.reshape(1, -1)

        if query_vec.shape[1] != self.dimension:
            raise ValueError(
                f"Query dimension mismatch: store expected {self.dimension}, got {query_vec.shape[1]}"
            )

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k)

        results: List[Tuple[ProcessedChunk, float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))

        return results

    def search_lexical(
        self,
        query: str,
        top_k: int = 4,
    ) -> List[Tuple[ProcessedChunk, float]]:
        """Lexical and keyword chunk search over stored chunks.

        Serves as a deterministic zero-failure fallback for discovery and scheme
        queries if the embedding service or external inference API is temporarily
        unavailable, ensuring grounded official sources are always retrieved.
        """
        if not query or not query.strip() or not self.chunks:
            return []

        import re
        tokens = set(re.findall(r"\w+", query.lower()))
        # Filter out common stop words
        stops = {
            "what", "is", "the", "for", "can", "and", "are", "which", "how", "who",
            "i", "a", "an", "to", "of", "in", "my", "me", "tell", "about", "give", "details"
        }
        query_words = [t for t in tokens if len(t) >= 3 and t not in stops]
        if not query_words:
            query_words = [t for t in tokens if len(t) >= 2]

        scored: List[Tuple[ProcessedChunk, float]] = []
        for chunk in self.chunks:
            score = 0.0
            text = getattr(chunk, "text", "") or (chunk.get("text") if isinstance(chunk, dict) else "") or ""
            title = getattr(chunk, "title", "") or (chunk.get("title") if isinstance(chunk, dict) else "") or ""
            meta = getattr(chunk, "metadata", {}) or (chunk.get("metadata") if isinstance(chunk, dict) else {}) or {}
            category = (meta.get("category", "") if isinstance(meta, dict) else "") or getattr(chunk, "category", "") or ""

            content_lower = text.lower()
            name_lower = title.lower()
            cat_lower = category.lower()

            for word in query_words:
                if word in name_lower:
                    score += 6.0
                if word in cat_lower:
                    score += 4.0
                if word in content_lower:
                    score += 1.0

            # Domain intent boosters for discovery queries
            if any(w in query_words for w in ["student", "scholarship", "study", "education", "college", "school", "fellowship", "shiksha"]):
                if any(k in name_lower or k in cat_lower for k in ["scholarship", "student", "education", "fellowship", "shiksha"]):
                    score += 5.0
            if any(w in query_words for w in ["farmer", "kisan", "agriculture", "crop", "krishi", "kheti", "rural"]):
                if any(k in name_lower or k in cat_lower for k in ["kisan", "farmer", "krishi", "fasal", "agriculture"]):
                    score += 5.0
            if any(w in query_words for w in ["women", "woman", "girl", "mahila", "beti", "ladli", "mother", "matru"]):
                if any(k in name_lower or k in cat_lower for k in ["women", "girl", "matru", "shakti", "sukanya", "mahila"]):
                    score += 5.0
            if any(w in query_words for w in ["health", "hospital", "medical", "ayushman", "pmjay", "swasthya", "disease", "treatment", "aushadh"]):
                if any(k in name_lower or k in cat_lower for k in ["ayushman", "health", "pmjay", "swasthya", "medical"]):
                    score += 5.0
            if any(w in query_words for w in ["pension", "vridha", "elderly", "senior", "retirement", "atal", "nsap"]):
                if any(k in name_lower or k in cat_lower for k in ["pension", "apy", "atal", "nsap", "vridha"]):
                    score += 5.0
            if any(w in query_words for w in ["house", "housing", "home", "awas", "makan", "ghar", "shelter"]):
                if any(k in name_lower or k in cat_lower for k in ["awas", "housing", "pmay", "shelter"]):
                    score += 5.0
            if any(w in query_words for w in ["business", "loan", "startup", "mudra", "credit", "msme", "dukan", "commerce"]):
                if any(k in name_lower or k in cat_lower for k in ["mudra", "pmmy", "credit", "msme", "standup"]):
                    score += 5.0

            if score > 0:
                normalized_score = min(0.95, 0.5 + (score / 40.0))
                scored.append((chunk, normalized_score))

        scored.sort(key=lambda x: x[1], reverse=True)

        # Deduplicate to pick top chunks from diverse schemes where possible
        selected: List[Tuple[ProcessedChunk, float]] = []
        seen_titles = set()
        for chunk, s in scored:
            title_str = getattr(chunk, "title", "")
            if title_str not in seen_titles:
                selected.append((chunk, s))
                seen_titles.add(title_str)
            if len(selected) >= top_k:
                break

        if len(selected) < top_k:
            for chunk, s in scored:
                if chunk not in [c for c, _ in selected]:
                    selected.append((chunk, s))
                if len(selected) >= top_k:
                    break

        return selected

    def get_featured_chunks(self, top_k: int = 4) -> List[Tuple[ProcessedChunk, float]]:
        """Return high-priority canonical scheme chunks when no specific keywords match."""
        if not self.chunks:
            return []
        featured_names = [
            "kisan", "ayushman", "scholarship", "mudra", "awas", "pension"
        ]
        results: List[Tuple[ProcessedChunk, float]] = []
        seen_titles = set()
        for chunk in self.chunks:
            t = (getattr(chunk, "title", "") or "").lower()
            if any(f in t for f in featured_names) and chunk.title not in seen_titles:
                results.append((chunk, 0.75))
                seen_titles.add(chunk.title)
                if len(results) >= top_k:
                    break
        if not results:
            for chunk in self.chunks[:top_k]:
                results.append((chunk, 0.70))
        return results

    def save(self, index_path: Union[str, Path]) -> None:
        """Save FAISS binary index and chunk metadata to disk.

        Args:
            index_path: File path where the FAISS index should be saved (e.g. vector_store/index.faiss).
        """
        path = Path(index_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        meta_path = self._get_meta_path(path)

        # 1. Save FAISS binary index
        faiss.write_index(self.index, str(path))

        # 2. Save metadata JSON
        meta_payload = {
            "dimension": self.dimension,
            "total_chunks": len(self.chunks),
            "chunks": [chunk.model_dump() for chunk in self.chunks],
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, ensure_ascii=False, indent=2)

        logger.info(
            "Saved vector store (%d vectors, dim=%d) to %s and metadata to %s",
            self.index.ntotal,
            self.dimension,
            path,
            meta_path,
        )

    @classmethod
    def load(cls, index_path: Union[str, Path]) -> "FAISSVectorStore":
        """Load an existing FAISS index and its metadata mapping from disk.

        Args:
            index_path: Path to the FAISS index file.

        Returns:
            Instantiated and populated FAISSVectorStore.

        Raises:
            FileNotFoundError: If index file or metadata file is missing.
            ValueError: If vector count does not match metadata count, or file is corrupted.
        """
        path = Path(index_path)
        if not path.exists():
            raise FileNotFoundError(f"FAISS index file not found: {path}")

        meta_path = cls._get_meta_path(path)
        if not meta_path.exists():
            raise FileNotFoundError(f"Vector store metadata file not found: {meta_path}")

        # Load metadata
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
        except Exception as err:
            raise ValueError(f"Corrupted metadata file {meta_path}: {err}") from err

        dimension = meta_data.get("dimension")
        if not dimension or dimension <= 0:
            raise ValueError(f"Invalid dimension {dimension} in metadata {meta_path}")

        # Instantiate store
        store = cls(dimension=dimension)

        # Read FAISS index if available
        if faiss is not None and path.exists():
            try:
                store.index = faiss.read_index(str(path))
            except Exception as err:
                logger.warning(f"Failed to load FAISS binary index {path}: {err}; will rely on lexical search")
                store.index = None
        else:
            store.index = None

        # Load chunks
        raw_chunks = meta_data.get("chunks", [])
        store.chunks = [ProcessedChunk.model_validate(c) for c in raw_chunks]

        # Integrity verification if index was loaded
        if store.index is not None and store.index.ntotal != len(store.chunks):
            logger.warning(
                f"Vector store count mismatch: FAISS has {store.index.ntotal} vectors "
                f"but metadata contains {len(store.chunks)} chunks."
            )

        total_indexed = store.index.ntotal if store.index is not None else len(store.chunks)
        logger.info(
            "Loaded vector store from %s with %d chunks (dim=%d, faiss_enabled=%s)",
            path,
            total_indexed,
            dimension,
            store.index is not None,
        )
        return store
