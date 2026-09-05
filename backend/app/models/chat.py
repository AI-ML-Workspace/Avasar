from typing import List, Optional
from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    """Source reference for a government scheme or official document."""
    title: str = Field(
        ...,
        description="Name of the government scheme or official document",
        examples=["Pradhan Mantri Awas Yojana (PMAY)"]
    )
    url: Optional[str] = Field(
        default=None,
        description="Official government portal or document URL",
        examples=["https://pmaymis.gov.in/"]
    )
    snippet: Optional[str] = Field(
        default=None,
        description="Relevant excerpt or description from the scheme knowledge base",
        examples=["PMAY provides central assistance to Urban Local Bodies and other implementing agencies for housing."]
    )
    score: Optional[float] = Field(
        default=None,
        description="Relevance or retrieval similarity score",
        examples=[0.89]
    )
    source_id: Optional[str] = Field(
        default=None,
        description="Identifier of the originating registered OfficialSource (e.g., 'nsp', 'pm_kisan')",
        examples=["pm_kisan"]
    )
    is_official: bool = Field(
        default=True,
        description="Strict official government domain verification status",
        examples=[True]
    )
    trust_level: Optional[str] = Field(
        default=None,
        description="Authority classification level of the source",
        examples=["primary_authoritative"]
    )
    classification: Optional[str] = Field(
        default=None,
        description="Government tier (e.g. central, national_portal, state_ut)",
        examples=["central"]
    )
    official_domain: Optional[str] = Field(
        default=None,
        description="Verified primary government domain host",
        examples=["pmkisan.gov.in"]
    )
    last_synced_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp when content was retrieved or last verified",
        examples=["2026-09-05T00:53:08.874756+00:00"]
    )


class ChatRequest(BaseModel):
    """Payload sent by the frontend to POST /api/chat."""
    message: str = Field(
        ...,
        min_length=1,
        description="User query in any Indian language or English",
        examples=["How do I apply for PM Kisan scheme?"]
    )
    language: Optional[str] = Field(
        default=None,
        description="Optional ISO 639-1 language code (e.g., 'en', 'hi', 'bn', 'te'). Auto-detected if omitted.",
        examples=["en"]
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for maintaining multi-turn context",
        examples=["conv_9f82d1c0"]
    )


class ChatResponse(BaseModel):
    """Response returned by POST /api/chat to the frontend."""
    answer: str = Field(
        ...,
        description="Generated conversational response",
        examples=["PM Kisan provides ₹6,000 per year to eligible farmer families in three equal installments."]
    )
    language: str = Field(
        ...,
        description="ISO 639-1 language code of the response text",
        examples=["en"]
    )
    sources: List[SourceItem] = Field(
        default_factory=list,
        description="List of verified scheme sources cited in the response"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation identifier for multi-turn tracking",
        examples=["conv_9f82d1c0"]
    )
