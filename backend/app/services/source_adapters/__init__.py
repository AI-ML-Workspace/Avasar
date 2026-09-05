import logging
from typing import Dict, Optional, Type

from app.models.source import OfficialSource
from app.services.source_adapters.base import (
    IngestionResult,
    IngestionSecurityError,
    RawDocument,
    SafeFetcher,
    SourceAdapter,
)
from app.services.source_adapters.pm_kisan import PMKisanSourceAdapter
from app.services.source_registry import SourceRegistry, get_source_registry

logger = logging.getLogger(__name__)

# Registry mapping source_id to concrete SourceAdapter implementations
_ADAPTER_MAP: Dict[str, Type[SourceAdapter]] = {
    "pm_kisan": PMKisanSourceAdapter,
}


def register_adapter_class(source_id: str, adapter_cls: Type[SourceAdapter]) -> None:
    """Register a concrete adapter implementation for a source_id."""
    _ADAPTER_MAP[source_id.strip().lower()] = adapter_cls


def get_adapter_for_source(
    source_id: str,
    registry: Optional[SourceRegistry] = None,
) -> Optional[SourceAdapter]:
    """Resolve and instantiate the appropriate SourceAdapter for a registered OfficialSource.

    Args:
        source_id: Registered source identifier (e.g., 'pm_kisan', 'myscheme').
        registry: Optional SourceRegistry instance.

    Returns:
        Instantiated SourceAdapter if an adapter is implemented, else None.
    """
    clean_id = source_id.strip().lower()
    reg = registry or get_source_registry()
    source: Optional[OfficialSource] = reg.get_source(clean_id)
    if not source:
        logger.warning("Source '%s' is not registered in Official Source Registry.", clean_id)
        return None

    adapter_cls = _ADAPTER_MAP.get(clean_id)
    if not adapter_cls:
        logger.info("No adapter implementation available yet for registered source '%s'.", clean_id)
        return None

    return adapter_cls(source=source)


__all__ = [
    "SourceAdapter",
    "SafeFetcher",
    "RawDocument",
    "IngestionResult",
    "IngestionSecurityError",
    "PMKisanSourceAdapter",
    "get_adapter_for_source",
    "register_adapter_class",
]
