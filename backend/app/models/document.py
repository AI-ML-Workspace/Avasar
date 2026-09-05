from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SchemeDocument(BaseModel):
    """Normalized representation of a raw government scheme document with provenance."""

    id: str = Field(..., description="Unique scheme identifier")
    title: str = Field(..., description="Official scheme name / title")
    url: Optional[str] = Field(
        default=None,
        description="Official government scheme portal or application link",
    )
    source_id: Optional[str] = Field(
        default=None,
        description="Identifier of the registered OfficialSource (e.g. 'pm_kisan', 'myscheme')",
    )
    source_name: str = Field(
        default="Government of India",
        description="Publisher, ministry, or department name",
    )
    official_source_url: Optional[str] = Field(
        default=None,
        description="Base authoritative URL of the official source portal",
    )
    source_type: Optional[str] = Field(
        default=None,
        description="Type/nature of official source (e.g. 'scheme_portal', 'aggregator')",
    )
    trust_level: Optional[str] = Field(
        default=None,
        description="Trust priority level (e.g. 'primary_authoritative')",
    )
    retrieved_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp when this document was fetched from the official source",
    )
    published_at: Optional[str] = Field(
        default=None,
        description="Date/timestamp when document was published or updated by the government",
    )
    content_hash: Optional[str] = Field(
        default=None,
        description="Deterministic SHA-256 hash of normalized content for deduplication",
    )
    document_type: str = Field(
        default="scheme_overview",
        description="Classification of document content (e.g. 'scheme_overview', 'guidelines', 'faq')",
    )
    version: int = Field(
        default=1,
        description="Revision number for tracking updates to the scheme content",
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
    source_id: Optional[str] = Field(
        default=None,
        description="Identifier of the originating registered OfficialSource",
    )
    source_name: str = Field(
        default="Government of India",
        description="Ministry or department source name",
    )
    official_source_url: Optional[str] = Field(
        default=None,
        description="Base authoritative URL of the official source portal",
    )
    source_type: Optional[str] = Field(
        default=None,
        description="Source classification type (e.g. 'scheme_portal', 'aggregator')",
    )
    trust_level: Optional[str] = Field(
        default=None,
        description="Authority level of the source",
    )
    retrieved_at: Optional[str] = Field(
        default=None,
        description="Timestamp when source content was retrieved",
    )
    published_at: Optional[str] = Field(
        default=None,
        description="Timestamp when document was officially published/updated",
    )
    content_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of parent document content",
    )
    document_type: str = Field(
        default="scheme_overview",
        description="Classification of document content",
    )
    version: int = Field(
        default=1,
        description="Document version number",
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
