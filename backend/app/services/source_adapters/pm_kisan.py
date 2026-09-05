import logging
import re
from html.parser import HTMLParser
from typing import List, Optional
from urllib.parse import urlparse

from app.models.document import SchemeDocument
from app.models.source import OfficialSource
from app.services.source_adapters.base import RawDocument, SourceAdapter

logger = logging.getLogger(__name__)


class _HTMLTextExtractor(HTMLParser):
    """Standard library HTML parser to cleanly extract text content."""

    def __init__(self):
        super().__init__()
        self.text_parts: List[str] = []
        self._ignore_stack: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() in ("script", "style", "noscript", "svg", "header", "footer"):
            self._ignore_stack.append(tag.lower())

    def handle_endtag(self, tag: str):
        if self._ignore_stack and self._ignore_stack[-1] == tag.lower():
            self._ignore_stack.pop()

    def handle_data(self, data: str):
        if not self._ignore_stack:
            clean = data.strip()
            if clean:
                self.text_parts.append(clean)


def extract_clean_text_from_html(html: str) -> str:
    """Extract clean, readable text from HTML markup."""
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = "\n".join(parser.text_parts)
    # Deduplicate excessive empty lines
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class PMKisanSourceAdapter(SourceAdapter):
    """Authoritative adapter for the PM-KISAN Central Government Scheme portal."""

    def __init__(self, source: OfficialSource):
        super().__init__(source=source)

    async def fetch(self, max_documents: Optional[int] = None) -> List[RawDocument]:
        """Fetch primary documents from pmkisan.gov.in.

        Retrieves official scheme portal text and operational e-KYC guidelines.
        """
        limit = max_documents or 5
        raw_docs: List[RawDocument] = []

        target_paths = [
            "/",
            "/KnowAboutEKYC.aspx",
        ]

        for path in target_paths[:limit]:
            target_url = f"{self.source.base_url.rstrip('/')}{path}"
            try:
                raw_doc = await self.fetcher.fetch(target_url)
                raw_docs.append(raw_doc)
            except Exception as err:
                logger.warning(f"Could not fetch target path '{path}' from PM-KISAN: {err}")

        return raw_docs

    def validate(self, raw_doc: RawDocument) -> bool:
        """Verify that the fetched document belongs to PM-KISAN and has meaningful content."""
        if raw_doc.status_code != 200:
            return False

        if not raw_doc.content or len(raw_doc.content.strip()) < 100:
            return False

        # Verify key official terms are present
        content_lower = raw_doc.content.lower()
        if not ("pm-kisan" in content_lower or "pm kisan" in content_lower or "kisan" in content_lower):
            logger.warning("PM-KISAN keyword verification failed on %s", raw_doc.url)
            return False

        return True

    def normalize(self, raw_doc: RawDocument) -> SchemeDocument:
        """Normalize the raw HTML page into a structured SchemeDocument."""
        clean_text = extract_clean_text_from_html(raw_doc.content)

        parsed = urlparse(raw_doc.url)
        path_name = parsed.path.strip("/").replace(".aspx", "").lower()
        sub_id = path_name if path_name else "overview"

        doc_id = f"pm_kisan_portal_{sub_id}"
        title = (
            "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) Official Portal"
            if sub_id == "overview"
            else f"PM-KISAN Official Guideline — {sub_id.replace('_', ' ').title()}"
        )

        return SchemeDocument(
            id=doc_id,
            title=title,
            url=raw_doc.url,
            source_id=self.source.source_id,
            source_name=self.source.name,
            official_source_url=self.source.base_url,
            retrieved_at=raw_doc.retrieved_at,
            published_at=None,
            document_type="portal_guideline",
            version=1,
            language="en",
            content=clean_text,
            metadata={
                "source_url": raw_doc.url,
                "ministry": self.source.ministry or "Ministry of Agriculture & Farmers Welfare",
                "classification": self.source.classification.value,
                "source_type": self.source.source_type.value,
            },
        )
