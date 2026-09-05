import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from urllib.parse import urlparse

from app.core.config import settings
from app.models.source import (
    GovernmentClassification,
    OfficialSource,
    SourceType,
    is_authorized_government_domain,
)

logger = logging.getLogger(__name__)


class SourceRegistry:
    """Maintainable registry of verified official Indian government knowledge sources.

    Ensures that only authoritative government domains (.gov.in, .nic.in, and verified
    statutory platforms) are recognized as valid sources for ingestion and citation.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self._config_path = (
            Path(config_path) if config_path else settings.resolved_sources_config_path
        )
        self._sources: Dict[str, OfficialSource] = {}
        self.reload()

    @property
    def config_path(self) -> Path:
        """Path to the registry configuration file."""
        return self._config_path

    def reload(self) -> int:
        """Load or reload all official sources from the configuration file.

        Returns:
            Count of successfully loaded sources.

        Raises:
            FileNotFoundError: If configuration file does not exist.
            ValueError: If configuration JSON is malformed or violates schema.
        """
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"Source registry configuration file not found at '{self._config_path}'."
            )

        with open(self._config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(
                f"Source registry configuration must be a JSON list of sources, got {type(data).__name__}."
            )

        loaded_sources: Dict[str, OfficialSource] = {}
        for entry in data:
            source = OfficialSource.model_validate(entry)
            loaded_sources[source.source_id] = source

        self._sources = loaded_sources
        logger.info("Loaded %d official sources from %s", len(self._sources), self._config_path.name)
        return len(self._sources)

    def register_source(self, source: OfficialSource) -> None:
        """Dynamically register or update an official source.

        Args:
            source: Validated OfficialSource instance.
        """
        self._sources[source.source_id] = source
        logger.info("Registered official source '%s' (%s)", source.source_id, source.base_url)

    def get_source(self, source_id: str) -> Optional[OfficialSource]:
        """Retrieve an official source by its unique identifier.

        Args:
            source_id: Source identifier (e.g. 'myscheme', 'pm_kisan').

        Returns:
            OfficialSource if found, else None.
        """
        return self._sources.get(source_id.strip().lower())

    def list_sources(
        self,
        enabled_only: bool = True,
        classification: Optional[Union[GovernmentClassification, str]] = None,
        source_type: Optional[Union[SourceType, str]] = None,
        state_or_ut: Optional[str] = None,
    ) -> List[OfficialSource]:
        """List registered official sources with optional filtering.

        Args:
            enabled_only: If True, only returns currently active sources.
            classification: Optional filter by Central / State / National Portal.
            source_type: Optional filter by Aggregator / Ministry / State / Scheme Portal.
            state_or_ut: Optional case-insensitive filter by State/UT name.

        Returns:
            List of matching OfficialSource objects.
        """
        results: List[OfficialSource] = []
        target_class = (
            classification.value.lower()
            if isinstance(classification, GovernmentClassification)
            else str(classification).lower()
        ) if classification else None

        target_type = (
            source_type.value.lower()
            if isinstance(source_type, SourceType)
            else str(source_type).lower()
        ) if source_type else None

        target_state = state_or_ut.strip().lower() if state_or_ut else None

        for source in self._sources.values():
            if enabled_only and not source.enabled:
                continue

            if target_class and source.classification.value != target_class:
                continue

            if target_type and source.source_type.value != target_type:
                continue

            if target_state:
                if not source.state_or_ut or source.state_or_ut.strip().lower() != target_state:
                    continue

            results.append(source)

        return results

    def get_allowed_domains(self, enabled_only: bool = True) -> Set[str]:
        """Collect all whitelisted hostnames/domains across registered sources."""
        domains: Set[str] = set()
        for source in self._sources.values():
            if enabled_only and not source.enabled:
                continue
            domains.update(source.allowed_domains)
        return domains

    def get_source_for_url(self, url: str) -> Optional[OfficialSource]:
        """Find the registered OfficialSource responsible for a given URL.

        Args:
            url: Any scheme portal or application URL.

        Returns:
            The matching OfficialSource if its domain is whitelisted, else None.
        """
        if not url or not str(url).strip():
            return None

        parsed = urlparse(str(url).strip())
        hostname = (parsed.hostname or parsed.netloc.split(":")[0]).lower()
        if not hostname:
            return None

        for source in self._sources.values():
            if not source.enabled:
                continue
            for domain in source.allowed_domains:
                if hostname == domain or hostname.endswith("." + domain):
                    return source

        return None

    def is_allowed_domain(self, domain_or_url: str) -> bool:
        """Check whether a domain or URL belongs to an enabled registered source.

        Args:
            domain_or_url: Hostname or full URL.

        Returns:
            True if domain is whitelisted by at least one enabled official source.
        """
        if not domain_or_url:
            return False

        clean = str(domain_or_url).strip().lower()
        if "://" in clean:
            parsed = urlparse(clean)
            hostname = parsed.hostname or parsed.netloc.split(":")[0]
        else:
            hostname = clean.split("/")[0].split(":")[0]

        if not hostname:
            return False

        # First verify it is a valid government domain structure
        if not is_authorized_government_domain(hostname):
            return False

        # Then verify it is registered in our authorized source registry
        for source in self._sources.values():
            if not source.enabled:
                continue
            for domain in source.allowed_domains:
                if hostname == domain or hostname.endswith("." + domain):
                    return True

        return False

    def validate_source_url(self, url: str) -> bool:
        """Strictly validate that a URL uses http/https and points to an official source."""
        if not url:
            return False
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https"):
            return False
        return self.is_allowed_domain(url)


# Global singleton registry instance
_source_registry_instance: Optional[SourceRegistry] = None


def get_source_registry() -> SourceRegistry:
    """Accessor for the singleton SourceRegistry instance."""
    global _source_registry_instance
    if _source_registry_instance is None:
        _source_registry_instance = SourceRegistry()
    return _source_registry_instance
