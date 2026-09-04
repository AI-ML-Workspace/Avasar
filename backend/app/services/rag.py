import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

from app.core.config import settings
from app.models.chat import SourceItem
from app.models.document import ProcessedChunk
from app.services.embedding import EmbeddingService, get_embedding_service
from app.services.vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


class RAGService:
    """RAG Retrieval Service connecting query embeddings to FAISS vector search.

    Performs:
        query text -> embedding -> FAISS cosine similarity search -> relevant scheme sources
    """

    def __init__(
        self,
        vector_store: Optional[FAISSVectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store_path: Optional[Union[str, Path]] = None,
    ):
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._vector_store_path = (
            Path(vector_store_path)
            if vector_store_path
            else settings.resolved_vector_store_path
        )

    @property
    def embedding_service(self) -> EmbeddingService:
        """Embedding service instance."""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    @property
    def vector_store(self) -> FAISSVectorStore:
        """FAISS vector store instance (lazy-loaded from disk if not injected)."""
        if self._vector_store is None:
            if not self._vector_store_path.exists():
                raise FileNotFoundError(
                    f"Vector store not found at '{self._vector_store_path}'. "
                    f"Run 'python scripts/build_vector_store.py' to build the index."
                )
            self._vector_store = FAISSVectorStore.load(self._vector_store_path)
        return self._vector_store

    def retrieve_chunks(
        self,
        query: str,
        top_k: int = 4,
    ) -> List[Tuple[ProcessedChunk, float]]:
        """Retrieve top-k scheme ProcessedChunks with similarity scores.

        Args:
            query: Citizen query string in any Indian language or English.
            top_k: Number of relevant scheme chunks to return.

        Returns:
            List of (ProcessedChunk, score) tuples ordered by descending cosine similarity.

        Raises:
            ValueError: If query is empty or top_k <= 0.
            FileNotFoundError: If vector store index has not been built yet.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        if top_k <= 0:
            raise ValueError(f"top_k must be a positive integer, got {top_k}")

        query_vec = self.embedding_service.embed_text(query.strip())
        return self.vector_store.search(query_vec, top_k=top_k)

    async def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> List[SourceItem]:
        """Retrieve top-k scheme sources formatted as SourceItem for API responses.

        Args:
            query: The citizen search query.
            top_k: Number of relevant scheme contexts to return.

        Returns:
            List of SourceItem references with scheme name, URL, snippet, and relevance score.
        """
        chunk_results = self.retrieve_chunks(query=query, top_k=top_k)

        source_items: List[SourceItem] = []
        for chunk, score in chunk_results:
            source_items.append(
                SourceItem(
                    title=chunk.title,
                    url=chunk.url,
                    snippet=chunk.text,
                    score=round(float(score), 4),
                )
            )

        return source_items
