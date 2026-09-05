from pathlib import Path
import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Project root is 3 levels above backend/app/core/config.py
ROOT_DIR = Path(__file__).resolve().parents[3]

# Load environment files from project root
# .env is the baseline, .env.local overrides for local development
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / ".env.local", override=True)


class Settings(BaseModel):
    """Centralized backend application settings.
    
    Loads configuration from root .env / .env.local.
    All secrets remain server-side only.
    """
    api_title: str = "Avasar API"
    api_description: str = "Language Agnostic Chatbot for Government Schemes"
    api_version: str = "0.1.0"

    # CORS origins allowed to communicate with the API
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ]
    )

    # Server-side LLM API keys (never exposed to frontend)
    groq_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))

    # LLM Provider selection and generation settings
    llm_provider: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "groq").lower()
    )
    groq_model: str = Field(
        default_factory=lambda: os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    )
    gemini_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    )
    openai_model: str = Field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    llm_temperature: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.1"))
    )
    llm_max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "1024"))
    )

    # Vector store & embeddings
    vector_store_path: str = Field(
        default_factory=lambda: os.getenv("VECTOR_STORE_PATH", "../vector_store/index.faiss")
    )
    embedding_model: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        )
    )
    # External embedding API configurations (for serverless deployments)
    hf_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
    )
    embedding_api_url: Optional[str] = Field(
        default_factory=lambda: os.getenv("EMBEDDING_API_URL")
    )

    # Language configuration
    default_language: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en")
    )

    # Ingestion & Chunking pipeline configuration
    raw_data_dir: str = Field(
        default_factory=lambda: os.getenv(
            "RAW_DATA_DIR",
            str(ROOT_DIR / "data" / "raw" / "schemes")
            if (ROOT_DIR / "data" / "raw" / "schemes").is_dir()
            else str(ROOT_DIR / "data" / "raw"),
        )
    )
    processed_data_dir: str = Field(
        default_factory=lambda: os.getenv("PROCESSED_DATA_DIR", str(ROOT_DIR / "data" / "processed"))
    )
    chunk_size: int = Field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "500"))
    )
    chunk_overlap: int = Field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100"))
    )

    # Official Source Registry configuration
    sources_config_path: Optional[str] = Field(
        default_factory=lambda: os.getenv("SOURCES_CONFIG_PATH")
    )

    # Official Source Ingestion Engine settings
    ingestion_timeout: float = Field(
        default_factory=lambda: float(os.getenv("INGESTION_TIMEOUT", "15.0"))
    )
    ingestion_max_documents: int = Field(
        default_factory=lambda: int(os.getenv("INGESTION_MAX_DOCUMENTS", "50"))
    )
    ingestion_max_response_bytes: int = Field(
        default_factory=lambda: int(os.getenv("INGESTION_MAX_RESPONSE_BYTES", str(5 * 1024 * 1024)))
    )
    ingestion_user_agent: str = Field(
        default_factory=lambda: os.getenv(
            "INGESTION_USER_AGENT",
            "AvasarGovBot/1.0 (+https://github.com/jaiyansh-4n6/Avasar; citizen-welfare-assistant)",
        )
    )
    ingestion_data_dir: str = Field(
        default_factory=lambda: os.getenv("INGESTION_DATA_DIR", str(ROOT_DIR / "data" / "ingested"))
    )
    ingestion_verify_ssl: bool = Field(
        default_factory=lambda: os.getenv("INGESTION_VERIFY_SSL", "false").lower() in ("1", "true")
    )

    @property
    def resolved_ingestion_data_dir(self) -> Path:
        """Resolve directory for fetched official government data."""
        p = Path(self.ingestion_data_dir)
        if p.is_absolute():
            return p
        return (ROOT_DIR / p).resolve()

    @property
    def resolved_sources_config_path(self) -> Path:
        """Resolve sources registry config path reliably."""
        if self.sources_config_path:
            p = Path(self.sources_config_path)
            if p.is_absolute():
                return p
            return (ROOT_DIR / p).resolve()
        return Path(__file__).resolve().parent / "sources.json"

    @property
    def resolved_processed_data_dir(self) -> Path:
        """Resolve directory for processed canonical corpus data."""
        p = Path(self.processed_data_dir)
        if p.is_absolute():
            return p
        return (ROOT_DIR / p).resolve()

    @property
    def resolved_raw_data_dir(self) -> Path:
        """Resolve directory for raw scheme data."""
        p = Path(self.raw_data_dir)
        if p.is_absolute():
            return p
        return (ROOT_DIR / p).resolve()

    @property
    def resolved_vector_store_path(self) -> Path:
        """Resolve vector_store_path reliably relative to project root or absolute path."""
        p = Path(self.vector_store_path)
        if p.is_absolute():
            return p
        # If relative to backend/ (e.g. "../vector_store/index.faiss"):
        if str(p).startswith(".."):
            return (ROOT_DIR / "backend" / p).resolve()
        return (ROOT_DIR / p).resolve()


settings = Settings()
