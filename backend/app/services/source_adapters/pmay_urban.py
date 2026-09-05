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


class PMAYUrbanSourceAdapter(SourceAdapter):
    """Authoritative adapter for Pradhan Mantri Awas Yojana - Urban (MoHUA)."""

    def __init__(self, source: OfficialSource):
        super().__init__(source=source)

    async def fetch(self, max_documents: Optional[int] = None) -> List[RawDocument]:
        """Fetch primary documents from pmay-urban.gov.in.

        Retrieves official overview, CLSS subsidy guidelines, and scheme FAQs.
        """
        limit = max_documents or 5
        raw_docs: List[RawDocument] = []

        target_paths = [
            "/",
            "/credit-linked-subsidy-scheme",
            "/faq",
        ]

        for path in target_paths[:limit]:
            target_url = f"{self.source.base_url.rstrip('/')}{path}"
            try:
                raw_doc = await self.fetcher.fetch(target_url)
                raw_docs.append(raw_doc)
            except Exception as err:
                logger.warning("Could not fetch target path '%s' from PMAY-U: %s", path, err)

        return raw_docs

    def validate(self, raw_doc: RawDocument) -> bool:
        """Verify that the fetched document belongs to PMAY-U and has meaningful content."""
        if raw_doc.status_code != 200:
            return False

        if not raw_doc.content or len(raw_doc.content.strip()) < 100:
            return False

        content_lower = raw_doc.content.lower()
        if not ("pmay" in content_lower or "awas" in content_lower or "housing" in content_lower):
            logger.warning("PMAY-U keyword verification failed on %s", raw_doc.url)
            return False

        return True

    def normalize(self, raw_doc: RawDocument) -> SchemeDocument:
        """Normalize raw HTML page into a structured SchemeDocument."""
        clean_text = extract_clean_text_from_html(raw_doc.content)

        parsed = urlparse(raw_doc.url)
        path_name = parsed.path.strip("/").lower()
        sub_id = path_name if path_name else "overview"

        doc_id = f"pmay_urban_portal_{sub_id.replace('-', '_')}"
        if sub_id == "overview":
            title = "Pradhan Mantri Awas Yojana - Urban (PMAY-U) Official Portal"
        elif sub_id == "credit-linked-subsidy-scheme":
            title = "PMAY-U Credit Linked Subsidy Scheme (CLSS) Guidelines"
        elif sub_id == "faq":
            title = "PMAY-U Frequently Asked Questions (FAQ) & Four Pillars"
        else:
            title = f"PMAY-U Official Document — {sub_id.replace('-', ' ').title()}"

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
                "ministry": self.source.ministry or "Ministry of Housing and Urban Affairs",
                "classification": self.source.classification.value,
                "source_type": self.source.source_type.value,
            },
        )
