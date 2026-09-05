from enum import Enum
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator


class GovernmentClassification(str, Enum):
    """Jurisdictional tier of the government authority."""
    CENTRAL = "central"
    STATE_UT = "state_ut"
    NATIONAL_PORTAL = "national_portal"


class SourceType(str, Enum):
    """Type/nature of the official digital source."""
    AGGREGATOR = "aggregator"               # e.g., myScheme, India.gov.in, data.gov.in
    MINISTRY_PORTAL = "ministry_portal"     # e.g., Ministry of Agriculture, MoHFW
    STATE_PORTAL = "state_portal"           # e.g., Karnataka Seva Sindhu, UP eDistrict
    SCHEME_PORTAL = "scheme_portal"         # e.g., pmkisan.gov.in, pmjay.gov.in
    OPEN_DATASET = "open_dataset"           # e.g., data.gov.in scheme catalogs


class TrustLevel(str, Enum):
    """Authority priority of the source."""
    PRIMARY_AUTHORITATIVE = "primary_authoritative"   # Official Ministry or Scheme Portal
    VERIFIED_AGGREGATOR = "verified_aggregator"       # Official National Platform (myScheme, India.gov.in)
    SECONDARY_OFFICIAL = "secondary_official"         # Quasi-government statutory/financial body


class IngestionMethod(str, Enum):
    """Placeholder ingestion strategy for the source."""
    API = "api"
    STRUCTURED_DATASET = "structured_dataset"
    SITEMAP_CRAWL = "sitemap_crawl"
    HTML_SCRAPE = "html_scrape"
    MANUAL = "manual"


class UpdateFrequency(str, Enum):
    """Placeholder cadence for updating knowledge from this source."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"


# Suffixes and exact domains strictly recognized as Indian official government infrastructure
_OFFICIAL_GOV_SUFFIXES = (
    ".gov.in",
    ".nic.in",
    ".ac.in",
    ".edu.in",
    ".res.in",
)

# Specific non-standard TLDs explicitly verified as official Indian statutory or public platforms
_SPECIAL_VERIFIED_GOV_DOMAINS = {
    "mudra.org.in",
    "jansamarth.in",
    "nsiindia.gov.in",
    "npscra.nsdl.co.in",
    "uidai.gov.in",
}


def is_authorized_government_domain(hostname: str) -> bool:
    """Validate whether a hostname belongs to an authorized Indian government domain.

    Rules:
    - Must end in an official government suffix (.gov.in, .nic.in, etc.)
    - Or match an explicitly whitelisted statutory domain (e.g. mudra.org.in, jansamarth.in)
    - Commercial or third-party domains (.com, .net, .org, .co, .io, blog platforms) are rejected.
    """
    if not hostname:
        return False

    clean_host = hostname.strip().lower()
    # Strip port if present
    clean_host = clean_host.split(":")[0]

    # Check special verified statutory domains
    if clean_host in _SPECIAL_VERIFIED_GOV_DOMAINS:
        return True
    for special in _SPECIAL_VERIFIED_GOV_DOMAINS:
        if clean_host.endswith("." + special):
            return True

    # Check official suffixes
    for suffix in _OFFICIAL_GOV_SUFFIXES:
        if clean_host.endswith(suffix):
            return True

    return False


class OfficialSource(BaseModel):
    """Data contract for an authoritative government knowledge source."""

    source_id: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="Unique kebab-case or snake-case identifier for the source",
        examples=["myscheme", "pm_kisan", "india_gov"]
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=256,
        description="Official human-readable name of the source or portal",
        examples=["myScheme Portal", "PM-KISAN Portal"]
    )
    base_url: str = Field(
        ...,
        description="Authoritative root URL of the portal",
        examples=["https://www.myscheme.gov.in/"]
    )
    allowed_domains: List[str] = Field(
        default_factory=list,
        description="List of exact hostnames/domains permitted for ingestion and links",
        examples=[["myscheme.gov.in", "www.myscheme.gov.in"]]
    )
    classification: GovernmentClassification = Field(
        ...,
        description="Central, State/UT, or National Portal classification",
        examples=[GovernmentClassification.CENTRAL]
    )
    source_type: SourceType = Field(
        ...,
        description="Aggregator, Ministry Portal, State Portal, or Scheme Portal",
        examples=[SourceType.AGGREGATOR]
    )
    trust_level: TrustLevel = Field(
        default=TrustLevel.PRIMARY_AUTHORITATIVE,
        description="Authoritative priority level for RAG confidence weighting",
        examples=[TrustLevel.PRIMARY_AUTHORITATIVE]
    )
    enabled: bool = Field(
        default=True,
        description="Whether this source is currently active for ingestion and citation"
    )
    ingestion_method: IngestionMethod = Field(
        default=IngestionMethod.STRUCTURED_DATASET,
        description="Planned ingestion strategy"
    )
    update_frequency: UpdateFrequency = Field(
        default=UpdateFrequency.WEEKLY,
        description="Recommended refresh cadence"
    )
    state_or_ut: Optional[str] = Field(
        default=None,
        description="Applicable State or UT name if classification is state_ut",
        examples=["Karnataka", "Uttar Pradesh"]
    )
    ministry: Optional[str] = Field(
        default=None,
        description="Governing Central Ministry or State Department",
        examples=["Ministry of Agriculture and Farmers Welfare"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Brief summary of the portal's scope and contents"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary platform-specific metadata"
    )

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[a-z0-9_-]+$", clean):
            raise ValueError(
                f"source_id '{v}' must be lowercase alphanumeric with hyphens or underscores."
            )
        return clean

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        clean = v.strip()
        parsed = urlparse(clean)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"base_url '{v}' must use http or https scheme.")
        if not parsed.netloc:
            raise ValueError(f"base_url '{v}' is missing a valid domain host.")

        hostname = parsed.hostname or parsed.netloc.split(":")[0]
        if not is_authorized_government_domain(hostname):
            raise ValueError(
                f"Domain '{hostname}' in base_url is not recognized as an authorized "
                f"Indian government domain (.gov.in, .nic.in, or verified statutory portal)."
            )
        return clean

    @field_validator("allowed_domains")
    @classmethod
    def validate_allowed_domains(cls, domains: List[str], info) -> List[str]:
        cleaned_domains: List[str] = []
        for d in domains:
            clean = d.strip().lower().split(":")[0]
            if not clean:
                continue
            if not is_authorized_government_domain(clean):
                raise ValueError(
                    f"Allowed domain '{clean}' is not an authorized Indian government domain."
                )
            cleaned_domains.append(clean)

        # If empty, automatically infer from base_url
        if not cleaned_domains and "base_url" in info.data:
            base_host = urlparse(info.data["base_url"]).hostname
            if base_host:
                cleaned_domains.append(base_host.lower())

        return cleaned_domains
