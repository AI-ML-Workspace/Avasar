import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

from app.core.config import settings
from app.models.chat import SourceItem
from app.models.document import ProcessedChunk
from app.models.source import is_authorized_government_domain
from app.services.embedding import EmbeddingService, get_embedding_service
from app.services.source_registry import SourceRegistry, get_source_registry
from app.services.source_sync import SourceSyncService
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
        registry: Optional[SourceRegistry] = None,
    ):
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._vector_store_path = (
            Path(vector_store_path)
            if vector_store_path
            else settings.resolved_vector_store_path
        )
        self._registry = registry
        self._health_cache = None

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

        results: List[Tuple[ProcessedChunk, float]] = []
        try:
            query_vec = self.embedding_service.embed_text(query.strip())
            results = self.vector_store.search(query_vec, top_k=top_k)
        except Exception as err:
            logger.warning("Embedding/vector search encountered error: %s; falling back to lexical search", err)
            results = []

        # If semantic search returned nothing or embedding failed, fall back to lexical ranking over canonical chunks
        if not results:
            results = self.vector_store.search_lexical(query.strip(), top_k=top_k)

        return results

    async def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> List[SourceItem]:
        """Retrieve top-k scheme sources formatted as SourceItem for API responses.

        Enriches every citation with verified domain integrity, trust level,
        government classification, and synchronization freshness timestamps.

        Args:
            query: The citizen search query.
            top_k: Number of relevant scheme contexts to return.

        Returns:
            List of SourceItem references with scheme name, URL, snippet, relevance score,
            and complete citation trust metadata.
        """
        chunk_results = self.retrieve_chunks(query=query, top_k=top_k)
        registry = self._registry or get_source_registry()

        if self._health_cache is None:
            try:
                self._health_cache = SourceSyncService().load_health()
            except Exception:
                self._health_cache = {}

        source_items: List[SourceItem] = []
        for chunk, score in chunk_results:
            source_url = chunk.url or chunk.official_source_url
            domain = None
            is_official = False

            if source_url:
                parsed = urlparse(source_url)
                domain = (parsed.hostname or parsed.netloc.split(":")[0]).lower()
                is_official = is_authorized_government_domain(domain)

            # Match registered source entry
            source = None
            if chunk.source_id:
                source = registry.get_source(chunk.source_id)
            elif source_url:
                source = registry.get_source_for_url(source_url)

            resolved_source_id = chunk.source_id or (source.source_id if source else None)

            # Resolve authority trust level
            if chunk.trust_level:
                trust_level = chunk.trust_level
            elif source:
                trust_level = source.trust_level.value
            elif is_official:
                trust_level = "primary_authoritative"
            else:
                trust_level = "unverified"

            # Resolve government tier classification
            if chunk.metadata and chunk.metadata.get("classification"):
                classification = chunk.metadata["classification"]
            elif source:
                classification = source.classification.value
            elif is_official:
                classification = "central"
            else:
                classification = None

            # Resolve synchronization freshness timestamp
            last_synced_at = chunk.retrieved_at
            if not last_synced_at and resolved_source_id and self._health_cache:
                h = self._health_cache.get(resolved_source_id)
                if h and h.last_synced_at:
                    last_synced_at = h.last_synced_at

            source_items.append(
                SourceItem(
                    title=chunk.title,
                    url=source_url,
                    snippet=chunk.text,
                    score=round(float(score), 4),
                    source_id=resolved_source_id,
                    is_official=is_official,
                    trust_level=trust_level,
                    classification=classification,
                    official_domain=domain,
                    last_synced_at=last_synced_at,
                )
            )

        return source_items
