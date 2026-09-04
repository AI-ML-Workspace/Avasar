import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for producing normalized multilingual sentence embeddings.

    Loads the model once (lazy-loaded singleton pattern) and outputs L2-normalized
    vectors so inner product directly computes cosine similarity.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[SentenceTransformer] = None
        self._dimension: Optional[int] = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the SentenceTransformer model once."""
        if self._model is None:
            logger.info("Loading SentenceTransformer model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            get_dim = getattr(self._model, "get_embedding_dimension", None) or getattr(
                self._model, "get_sentence_embedding_dimension"
            )
            self._dimension = int(get_dim())
        return self._model

    @property
    def dimension(self) -> int:
        """Embedding vector dimension."""
        if self._dimension is None:
            _ = self.model
        return self._dimension  # type: ignore

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string into a normalized 1D float32 numpy array.

        Args:
            text: Input string to embed.

        Returns:
            Normalized 1D numpy array of shape (dimension,).

        Raises:
            ValueError: If text is empty or whitespace-only.
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty or whitespace-only text.")

        vec = self.model.encode(
            text.strip(),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.array(vec, dtype=np.float32)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed a list of text strings into a 2D float32 numpy array.

        Args:
            texts: List of text strings to embed.
            batch_size: Batch size for sentence-transformer inference.

        Returns:
            Normalized 2D numpy array of shape (N, dimension).

        Raises:
            ValueError: If texts list is empty.
        """
        if not texts:
            raise ValueError("Texts list cannot be empty for batch embedding.")

        cleaned = [t.strip() if t and t.strip() else " " for t in texts]
        embeddings = self.model.encode(
            cleaned,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 50,
        )
        return np.array(embeddings, dtype=np.float32)


# Default singleton instance
_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service(model_name: Optional[str] = None) -> EmbeddingService:
    """Get or create singleton EmbeddingService instance."""
    global _embedding_service_instance
    if _embedding_service_instance is None or (
        model_name and _embedding_service_instance.model_name != model_name
    ):
        _embedding_service_instance = EmbeddingService(model_name=model_name)
    return _embedding_service_instance
