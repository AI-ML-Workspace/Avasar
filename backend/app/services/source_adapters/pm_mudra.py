import logging
from typing import List, Optional
from urllib.parse import urlparse

from app.models.document import SchemeDocument
from app.models.source import OfficialSource
from app.services.source_adapters.base import (
    RawDocument,
    SourceAdapter,
    extract_clean_text_from_html,
)

logger = logging.getLogger(__name__)


class PMMudraSourceAdapter(SourceAdapter):
    """Authoritative adapter for Pradhan Mantri MUDRA Yojana (PMMY)."""

    def __init__(self, source: OfficialSource):
        super().__init__(source=source)

    async def fetch(self, max_documents: Optional[int] = None) -> List[RawDocument]:
        """Fetch primary documents from mudra.org.in.

        Retrieves official overview, loan categories (Shishu, Kishor, Tarun, TarunPlus),
        and PMMY application guidelines.
        """
        limit = max_documents or 5
        raw_docs: List[RawDocument] = []

        target_paths = [
            "/",
            "/Home/PMMY",
        ]

        for path in target_paths[:limit]:
            target_url = f"{self.source.base_url.rstrip('/')}{path}"
            try:
                raw_doc = await self.fetcher.fetch(target_url)
                raw_docs.append(raw_doc)
            except Exception as err:
                logger.warning("Could not fetch target path '%s' from MUDRA: %s", path, err)

        return raw_docs

    def validate(self, raw_doc: RawDocument) -> bool:
        """Verify that the fetched document belongs to MUDRA and has meaningful content."""
        if raw_doc.status_code != 200:
            return False

        if not raw_doc.content or len(raw_doc.content.strip()) < 100:
            return False

        content_lower = raw_doc.content.lower()
        if not ("mudra" in content_lower or "pmmy" in content_lower or "shishu" in content_lower or "tarun" in content_lower):
            logger.warning("MUDRA keyword verification failed on %s", raw_doc.url)
            return False

        return True

    def normalize(self, raw_doc: RawDocument) -> SchemeDocument:
        """Normalize raw HTML page into a structured SchemeDocument."""
        clean_text = extract_clean_text_from_html(raw_doc.content)

        parsed = urlparse(raw_doc.url)
        path_name = parsed.path.strip("/").lower().replace("home/", "")
        sub_id = path_name if path_name else "overview"

        doc_id = f"pm_mudra_portal_{sub_id.replace('-', '_')}"
        if sub_id == "overview":
            title = "Pradhan Mantri MUDRA Yojana (PMMY) Official Portal & Loan Categories"
        elif sub_id == "pmmy":
            title = "Pradhan Mantri MUDRA Yojana Guidelines & Udyamimitra Application Process"
        else:
            title = f"MUDRA Official Document — {sub_id.replace('-', ' ').title()}"

        return SchemeDocument(
            id=doc_id,
            title=title,
            url=raw_doc.url,
            source_id=self.source.source_id,
            source_name=self.source.name,
            official_source_url=self.source.base_url,
            source_type=self.source.source_type.value,
            trust_level=self.source.trust_level.value,
            retrieved_at=raw_doc.retrieved_at,
            published_at=None,
            document_type="portal_guideline",
            version=1,
            language="en",
            content=clean_text,
            metadata={
                "source_url": raw_doc.url,
                "ministry": self.source.ministry or "Department of Financial Services, Ministry of Finance",
                "classification": self.source.classification.value,
                "source_type": self.source.source_type.value,
            },
        )
