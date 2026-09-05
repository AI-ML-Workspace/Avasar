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
