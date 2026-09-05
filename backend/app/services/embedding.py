import logging
import os
from typing import Any, List, Optional
import httpx
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# Ensure serverless environments cache models/tokens in /tmp, not the deployment bundle
os.environ.setdefault("HF_HOME", "/tmp/huggingface")
os.environ.setdefault("TORCH_HOME", "/tmp/torch")


class EmbeddingService:
    """Service for producing normalized multilingual sentence embeddings.

    Supports both local execution via SentenceTransformer and remote execution
    via external embedding APIs (e.g. Hugging Face Serverless Inference API)
    for lightweight serverless deployments where bundling heavy PyTorch/CUDA
    dependencies would exceed function size limits.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[Any] = None
        self._dimension: Optional[int] = None

    @property
    def model(self) -> Any:
        """Lazy-load the local SentenceTransformer model if available."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading local SentenceTransformer model: %s", self.model_name)
                self._model = SentenceTransformer(self.model_name)
                get_dim = getattr(self._model, "get_embedding_dimension", None) or getattr(
                    self._model, "get_sentence_embedding_dimension", None
                )
                if get_dim:
                    self._dimension = int(get_dim())
            except ImportError:
                logger.info(
                    "sentence-transformers not installed locally; using external embedding service."
                )
                self._model = None
            except Exception as err:
                logger.warning(
                    "Failed to load local SentenceTransformer (%s); falling back to external API: %s",
                    self.model_name,
                    err,
                )
                self._model = None
        return self._model

    @property
    def dimension(self) -> int:
        """Embedding vector dimension (768 for paraphrase-multilingual-mpnet-base-v2)."""
        if self._dimension is None:
            if self.model is not None:
                get_dim = getattr(self.model, "get_embedding_dimension", None) or getattr(
                    self.model, "get_sentence_embedding_dimension", None
                )
                if get_dim:
                    self._dimension = int(get_dim())
            if self._dimension is None:
                # Default dimension for MPNet multilingual embeddings
                self._dimension = 768
        return self._dimension

    def _embed_via_external_api(self, text: str) -> np.ndarray:
        """Fetch embedding from configured external API or Hugging Face Inference API."""
        api_url = settings.embedding_api_url
        token = settings.hf_token

        headers: dict = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        urls_to_try = []
        if api_url:
            urls_to_try.append(api_url)
        else:
            urls_to_try.extend([
                f"https://router.huggingface.co/hf-inference/models/{self.model_name}",
                f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}",
            ])

        payload = {"inputs": text.strip()}

        with httpx.Client(timeout=15.0) as client:
            last_err = None
            for url in urls_to_try:
                try:
                    resp = client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        # Some endpoints return 2D [[...]], unwrap if needed
                        if isinstance(data, list) and data and isinstance(data[0], list):
                            data = data[0]
                        vec = np.array(data, dtype=np.float32)
                        norm = np.linalg.norm(vec)
                        if norm > 0:
                            vec = vec / norm
                        return vec
                    else:
                        last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
                except Exception as err:
                    last_err = str(err)
                    continue

        raise RuntimeError(
            f"External embedding service failed for '{self.model_name}'. "
            f"Set HF_TOKEN or EMBEDDING_API_URL in your environment variables. Error: {last_err}"
        )

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

        # If local SentenceTransformer model is available, use it
        if self.model is not None:
            vec = self.model.encode(
                text.strip(),
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return np.array(vec, dtype=np.float32)

        # In serverless/cloud runtime, load from external embedding source
        return self._embed_via_external_api(text)

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

        if self.model is not None:
            cleaned = [t.strip() if t and t.strip() else " " for t in texts]
            embeddings = self.model.encode(
                cleaned,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=len(texts) > 50,
            )
            return np.array(embeddings, dtype=np.float32)

        # External fallback: embed each text individually
        results = [self.embed_text(t) for t in texts]
        return np.vstack(results)


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
