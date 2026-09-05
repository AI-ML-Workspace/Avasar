import logging
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.models.source import OfficialSourcePublic, is_authorized_government_domain
from app.services.source_registry import SourceRegistry, get_source_registry
from app.services.source_sync import SourceSyncService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schemes", tags=["schemes"])


class OfficialSourcesResponse(BaseModel):
    """List of verified official Indian government knowledge sources."""
    sources: List[OfficialSourcePublic] = Field(
        ...,
        description="Public metadata and synchronization health for registered official government portals",
    )


def get_source_sync_service() -> SourceSyncService:
    """Dependency provider for SourceSyncService."""
    return SourceSyncService()


@router.get(
    "/sources",
    response_model=OfficialSourcesResponse,
    status_code=status.HTTP_200_OK,
    summary="List official government scheme sources and sync health",
    description="Returns public trust metadata and synchronization health for verified Indian government portals.",
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved official government sources with trust metadata"
        },
    },
)
async def get_official_sources(
    registry: SourceRegistry = Depends(get_source_registry),
    sync_service: SourceSyncService = Depends(get_source_sync_service),
) -> OfficialSourcesResponse:
    """Return safe public-facing metadata and freshness status for all registered official sources.

    Strict security guarantees:
    - Never exposes internal file paths, environment variables, or secrets.
    - Accurately classifies government domain verification status.
    - Pulls latest sync status from persistent health records.
    """
    health_records = sync_service.load_health()
    sources = registry.list_sources(enabled_only=True)

    public_sources: List[OfficialSourcePublic] = []
    for src in sources:
        h = health_records.get(src.source_id)
        last_synced = h.last_synced_at if h else None
        status_val = h.last_sync_status.lower() if h else "unknown"

        public_meta = src.to_public_metadata(
            last_synced_at=last_synced,
            sync_status=status_val,
        )
        public_sources.append(public_meta)

    return OfficialSourcesResponse(sources=public_sources)


class SchemeDetail(BaseModel):
    """Complete public metadata for a verified government scheme."""
    slug: str
    name: str
    category: str
    image: str = "/logo.png"
    summary: str
    description: str
    eligibility: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    howToApply: List[str] = Field(default_factory=list)
    whereToApply: str = ""
    conditions: List[str] = Field(default_factory=list)
    source: dict = Field(default_factory=dict)


class SchemesListResponse(BaseModel):
    """List of all curated government schemes."""
    total_schemes: int
    categories: List[str]
    schemes: List[SchemeDetail]


CATEGORY_IMAGE_MAP = {
    "Farmers": "/images/categories/agriculture.svg",
    "Students": "/images/categories/education.svg",
    "Women": "/images/categories/women.svg",
    "Healthcare": "/images/categories/healthcare.svg",
    "Housing": "/images/categories/housing.svg",
    "Employment": "/images/categories/employment.svg",
    "Social Security": "/images/categories/social.svg",
    "Small Businesses": "/images/categories/business.svg",
    "Financial Support": "/images/categories/financial.svg",
}

STANDARD_CATEGORIES = [
    "Students",
    "Farmers",
    "Women",
    "Healthcare",
    "Housing",
    "Employment",
    "Financial Support",
    "Small Businesses",
    "Social Security",
]


def _normalize_category(raw_cat: str) -> str:
    c = (raw_cat or "").lower()
    if any(k in c for k in ["farmer", "agri", "kisan", "crop", "rural dev"]):
        return "Farmers"
    if any(k in c for k in ["student", "scholarship", "education", "fellowship", "shiksha"]):
        return "Students"
    if any(k in c for k in ["women", "girl", "matru", "mahila"]):
        return "Women"
    if any(k in c for k in ["health", "hospital", "medical", "aushadh", "indradhanush"]):
        return "Healthcare"
    if any(k in c for k in ["housing", "shelter", "awas", "urban"]):
        return "Housing"
    if any(k in c for k in ["employ", "skill", "training", "kaushalya", "intern", "naps"]):
        return "Employment"
    if any(k in c for k in ["social security", "pension", "disability", "elderly", "nsap"]):
        return "Social Security"
    if any(k in c for k in ["business", "msme", "credit", "mudra", "cgtmse", "startup", "entrepreneur", "commerce"]):
        return "Small Businesses"
    if any(k in c for k in ["financial", "bank", "insurance", "savings", "subvention", "fund"]):
        return "Financial Support"
    return "Social Security"


_CACHED_SCHEMES: Optional[List[SchemeDetail]] = None


def load_all_schemes() -> List[SchemeDetail]:
    """Load and parse all canonical government schemes from storage."""
    global _CACHED_SCHEMES
    if _CACHED_SCHEMES is not None:
        return _CACHED_SCHEMES

    import json
    from app.core.config import settings

    raw_dir = settings.resolved_raw_data_dir
    scheme_files = sorted(list(raw_dir.glob("*.json")))

    results: List[SchemeDetail] = []
    seen_slugs = set()

    for p in scheme_files:
        if p.name == "sample_schemes.json":
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            continue

        slug = p.stem.replace("_", "-")
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        name = raw.get("scheme_name", p.stem.replace("_", " ").title())
        cat = _normalize_category(raw.get("category", ""))
        image = CATEGORY_IMAGE_MAP.get(cat, "/logo.png")

        desc = raw.get("description", "")
        summary = desc.split(".")[0] + "." if "." in desc else desc

        elig = raw.get("eligibility", [])
        if isinstance(elig, str):
            elig = [elig]

        app_process = raw.get("application_process", [])
        if isinstance(app_process, str):
            how_to = [app_process]
            where_to = app_process[:150]
        elif isinstance(app_process, list):
            how_to = app_process
            where_to = app_process[0][:150] if app_process else ""
        else:
            how_to, where_to = [], ""

        results.append(
            SchemeDetail(
                slug=slug,
                name=name,
                category=cat,
                image=image,
                summary=summary,
                description=desc,
                eligibility=elig,
                benefits=raw.get("benefits", []) if isinstance(raw.get("benefits"), list) else [str(raw.get("benefits"))],
                documents=raw.get("documents_required", []) if isinstance(raw.get("documents_required"), list) else [str(raw.get("documents_required"))],
                howToApply=how_to,
                whereToApply=where_to,
                conditions=raw.get("important_conditions", []) if isinstance(raw.get("important_conditions"), list) else [],
                source={
                    "label": raw.get("official_source") or raw.get("provider") or "Official Portal",
                    "url": raw.get("official_source_url") or "",
                },
            )
        )

    _CACHED_SCHEMES = results
    return results


@router.get(
    "",
    response_model=SchemesListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all canonical curated government schemes",
    description="Returns public metadata for all verified government schemes across categories.",
)
async def list_schemes(category: Optional[str] = None) -> SchemesListResponse:
    """Return all available schemes, optionally filtered by category."""
    all_schemes = load_all_schemes()
    if category:
        filtered = [s for s in all_schemes if s.category.lower() == category.lower()]
    else:
        filtered = all_schemes

    return SchemesListResponse(
        total_schemes=len(filtered),
        categories=STANDARD_CATEGORIES,
        schemes=filtered,
    )


@router.get(
    "/{slug}",
    response_model=SchemeDetail,
    status_code=status.HTTP_200_OK,
    summary="Get single scheme by slug",
    description="Returns full public details for an individual government scheme.",
)
async def get_scheme_by_slug(slug: str) -> SchemeDetail:
    """Return detailed information for a single scheme."""
    from fastapi import HTTPException
    all_schemes = load_all_schemes()
    for s in all_schemes:
        if s.slug == slug:
            return s
    raise HTTPException(status_code=404, detail=f"Scheme '{slug}' not found")
