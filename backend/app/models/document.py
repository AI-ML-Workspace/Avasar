from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SchemeDocument(BaseModel):
    """Normalized representation of a raw government scheme document."""

    id: str = Field(..., description="Unique scheme identifier")
    title: str = Field(..., description="Official scheme name / title")
    url: Optional[str] = Field(
        default=None,
        description="Official government scheme portal or application link",
    )
    source_name: str = Field(
        default="Government of India",
        description="Publisher, ministry, or department name",
    )
    language: Optional[str] = Field(
        default="en",
        description="Language code of the document content",
    )
    content: str = Field(
        ...,
        description="Full extracted or aggregated text body of the scheme",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary scheme attributes (e.g. ministry, category, eligibility criteria)",
    )


class ProcessedChunk(BaseModel):
    """Deterministic chunk of a scheme document for vector indexing and citation."""

    chunk_id: str = Field(
        ...,
        description="Unique deterministic chunk ID (e.g., scheme_id#chunk_idx)",
    )
    scheme_id: str = Field(
        ...,
        description="ID of the parent scheme document",
    )
    title: str = Field(
        ...,
        description="Scheme name / title for source citation",
    )
    url: Optional[str] = Field(
        default=None,
        description="Official source portal URL for citation",
    )
    source_name: str = Field(
        default="Government of India",
        description="Ministry or department source name",
    )
    language: Optional[str] = Field(
        default="en",
        description="Document language code",
    )
    chunk_index: int = Field(
        ...,
        description="0-indexed position within the parent document's chunks",
    )
    total_chunks: int = Field(
        ...,
        description="Total count of chunks generated from the parent document",
    )
    text: str = Field(
        ...,
        description="Chunk text content for embedding and RAG context retrieval",
    )
    char_length: int = Field(
        ...,
        description="Character count of chunk text",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Preserved scheme metadata from parent document",
    )
