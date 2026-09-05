import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.models.document import ProcessedChunk, SchemeDocument
from app.models.source import OfficialSource, is_authorized_government_domain
from app.services.chunking import chunk_document

logger = logging.getLogger(__name__)


class IngestionSecurityError(Exception):
    """Raised when an ingestion request violates domain or SSRF security policies."""
    pass


@dataclass
class RawDocument:
    """Raw fetched content and network provenance from an official source."""
    url: str
    content: str
    content_type: str
    status_code: int
    retrieved_at: str
    content_hash: str
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class IngestionResult:
    """Summary of an adapter ingestion run."""
    source_id: str
    status: str  # "SUCCESS", "FAILED", "NOT_IMPLEMENTED"
    documents_fetched: int = 0
    documents_changed: int = 0
    documents_unchanged: int = 0
    documents_rejected: int = 0
    chunks_created: int = 0
    http_status: Optional[int] = None
    errors: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "status": self.status,
            "documents_fetched": self.documents_fetched,
            "documents_changed": self.documents_changed,
            "documents_unchanged": self.documents_unchanged,
            "documents_rejected": self.documents_rejected,
            "chunks_created": self.chunks_created,
            "http_status": self.http_status,
            "errors": self.errors,
            "output_files": self.output_files,
        }


from html.parser import HTMLParser
import re


class _HTMLTextExtractor(HTMLParser):
    """Standard library HTML parser to cleanly extract text content."""

    def __init__(self):
        super().__init__()
        self.text_parts: List[str] = []
        self._ignore_stack: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() in ("script", "style", "noscript", "svg", "header", "footer", "nav"):
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
    """Extract clean, readable text from HTML markup, stripping scripts, CSS, and navigation."""
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = "\n".join(parser.text_parts)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class SafeFetcher:
    """HTTP client enforcing SSRF protection and authorized government domain verification."""

    def __init__(
        self,
        allowed_domains: List[str],
        timeout: Optional[float] = None,
        max_response_bytes: Optional[int] = None,
        user_agent: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
    ):
        self.allowed_domains: Set[str] = {d.strip().lower() for d in allowed_domains if d.strip()}
        self.timeout = timeout if timeout is not None else settings.ingestion_timeout
        self.max_response_bytes = (
            max_response_bytes if max_response_bytes is not None else settings.ingestion_max_response_bytes
        )
        self.user_agent = user_agent if user_agent is not None else settings.ingestion_user_agent
        self.verify_ssl = (
            verify_ssl if verify_ssl is not None else getattr(settings, "ingestion_verify_ssl", False)
        )

    def validate_url(self, url: str) -> str:
        """Validate URL protocol and ensure destination domain is allowed.

        Raises:
            IngestionSecurityError: If URL fails validation or domain is unauthorized.
        """
        if not url or not str(url).strip():
            raise IngestionSecurityError("URL cannot be empty.")

        clean_url = str(url).strip()
        parsed = urlparse(clean_url)
        if parsed.scheme not in ("http", "https"):
            raise IngestionSecurityError(f"Unsupported scheme '{parsed.scheme}' for URL '{clean_url}'.")

        hostname = (parsed.hostname or parsed.netloc.split(":")[0]).lower()
        if not hostname:
            raise IngestionSecurityError(f"Missing host in URL '{clean_url}'.")

        # Global official check
        if not is_authorized_government_domain(hostname):
            raise IngestionSecurityError(
                f"Unauthorized non-government host '{hostname}'. Expected official Indian government domain."
            )

        # Source-specific domain whitelist check
        is_whitelisted = False
        for allowed in self.allowed_domains:
            if hostname == allowed or hostname.endswith("." + allowed):
                is_whitelisted = True
                break

        if not is_whitelisted:
            raise IngestionSecurityError(
                f"Host '{hostname}' is not in source allowed_domains: {sorted(self.allowed_domains)}"
            )

        return clean_url

    async def fetch(self, url: str) -> RawDocument:
        """Safely fetch a URL with SSRF protection and redirect destination validation.

        Args:
            url: Target URL to retrieve.

        Returns:
            RawDocument with response text and metadata.

        Raises:
            IngestionSecurityError: If initial URL or any redirect URL targets an unauthorized domain.
            httpx.HTTPError: If network or HTTP status failure occurs.
        """
        validated_url = self.validate_url(url)
        headers = {"User-Agent": self.user_agent, "Accept": "text/html,application/json,application/xml,*/*"}

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=5,
            verify=self.verify_ssl,
        ) as client:
            resp = await client.get(validated_url, headers=headers)

            # Security: Verify that final URL after redirects still belongs to allowed domains
            final_url = str(resp.url)
            try:
                self.validate_url(final_url)
            except IngestionSecurityError as err:
                raise IngestionSecurityError(
                    f"Redirect led to unauthorized destination '{final_url}': {err}"
                ) from err

            resp.raise_for_status()

            content_len = len(resp.content)
            if content_len > self.max_response_bytes:
                raise ValueError(
                    f"Response size ({content_len} bytes) exceeded maximum allowed limit ({self.max_response_bytes} bytes)."
                )

            text_content = resp.text
            content_hash = hashlib.sha256(text_content.encode("utf-8")).hexdigest()
            retrieved_at = datetime.now(timezone.utc).isoformat()

            return RawDocument(
                url=final_url,
                content=text_content,
                content_type=resp.headers.get("content-type", ""),
                status_code=resp.status_code,
                retrieved_at=retrieved_at,
                content_hash=content_hash,
                headers=dict(resp.headers),
            )


class SourceAdapter(ABC):
    """Abstract base adapter for official government source ingestion."""

    def __init__(self, source: OfficialSource, fetcher: Optional[SafeFetcher] = None):
        self.source = source
        self.fetcher = fetcher or SafeFetcher(allowed_domains=source.allowed_domains)

    @abstractmethod
    async def fetch(self, max_documents: Optional[int] = None) -> List[RawDocument]:
        """Fetch raw documents from the official source."""
        pass

    @abstractmethod
    def validate(self, raw_doc: RawDocument) -> bool:
        """Validate that the raw document content is genuine and non-empty."""
        pass

    @abstractmethod
    def normalize(self, raw_doc: RawDocument) -> SchemeDocument:
        """Convert a validated raw document into a normalized SchemeDocument."""
        pass

    @staticmethod
    def calculate_content_hash(text: str) -> str:
        """Deterministic SHA-256 hash of normalized text for deduplication."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def load_manifest(self, manifest_file: Path) -> Dict[str, Any]:
        """Load source ingestion state manifest if it exists."""
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as err:
                logger.warning(f"Could not parse manifest at {manifest_file}: {err}")
        return {"source_id": self.source.source_id, "documents": {}}

    def save_manifest(self, manifest_file: Path, data: Dict[str, Any]) -> None:
        """Save source ingestion state manifest."""
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def ingest(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        max_documents: Optional[int] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        dry_run: bool = False,
    ) -> IngestionResult:
        """Execute the full ingestion pipeline for this official source.

        Pipeline:
            fetch -> validate -> content_hash & deduplicate -> normalize -> chunk -> save
        """
        c_size = chunk_size if chunk_size is not None else settings.chunk_size
        c_overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
        out_base = (
            Path(output_dir) if output_dir else settings.resolved_ingestion_data_dir
        ) / self.source.source_id

        manifest_file = out_base / "manifest.json"
        manifest = self.load_manifest(manifest_file)
        doc_registry: Dict[str, str] = manifest.get("documents", {})

        result = IngestionResult(source_id=self.source.source_id, status="SUCCESS")

        try:
            raw_docs = await self.fetch(max_documents=max_documents)
            result.http_status = raw_docs[0].status_code if raw_docs else 200
        except Exception as err:
            logger.error(f"Failed to fetch from {self.source.source_id}: {err}")
            result.status = "FAILED"
            status_code = getattr(getattr(err, "response", None), "status_code", None)
            result.http_status = status_code
            result.errors.append(str(err))
            return result

        result.documents_fetched = len(raw_docs)
        new_or_updated_docs: List[SchemeDocument] = []
        new_or_updated_chunks: List[ProcessedChunk] = []

        for raw_doc in raw_docs:
            # 1. Validation
            try:
                if not self.validate(raw_doc):
                    result.documents_rejected += 1
                    continue
            except Exception as val_err:
                logger.warning(f"Validation failed for {raw_doc.url}: {val_err}")
                result.documents_rejected += 1
                result.errors.append(f"Validation error ({raw_doc.url}): {val_err}")
                continue

            # 2. Normalization
            try:
                scheme_doc = self.normalize(raw_doc)
            except Exception as norm_err:
                logger.error(f"Normalization failed for {raw_doc.url}: {norm_err}")
                result.errors.append(f"Normalization error ({raw_doc.url}): {norm_err}")
                continue

            # 3. Deterministic Content Hashing & Deduplication
            content_hash = self.calculate_content_hash(scheme_doc.content)
            scheme_doc.content_hash = content_hash

            previous_hash = doc_registry.get(scheme_doc.id)
            if previous_hash == content_hash:
                # Content is identical to previous run -> deduplicated
                result.documents_unchanged += 1
                continue

            # Content is new or changed
            result.documents_changed += 1
            doc_registry[scheme_doc.id] = content_hash
            new_or_updated_docs.append(scheme_doc)

            # 4. Chunking
            chunks = chunk_document(
                doc=scheme_doc,
                chunk_size=c_size,
                chunk_overlap=c_overlap,
            )
            new_or_updated_chunks.extend(chunks)

        result.chunks_created = len(new_or_updated_chunks)

        # 5. Persistence (unless dry_run)
        if not dry_run and (new_or_updated_docs or not manifest_file.exists()):
            out_base.mkdir(parents=True, exist_ok=True)
            doc_file = out_base / "schemes.jsonl"
            chunk_file = out_base / "chunks.jsonl"

            # Load existing docs to cleanly replace updated docs without preserving stale versions
            existing_docs: Dict[str, Dict[str, Any]] = {}
            if doc_file.exists():
                try:
                    with open(doc_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                d = json.loads(line)
                                existing_docs[d["id"]] = d
                except Exception as err:
                    logger.warning("Could not read existing doc_file %s: %s", doc_file, err)

            for d in new_or_updated_docs:
                existing_docs[d.id] = d.model_dump()

            # Rewrite schemes.jsonl atomically
            temp_doc_file = out_base / "schemes.jsonl.tmp"
            with open(temp_doc_file, "w", encoding="utf-8") as f:
                for d_data in existing_docs.values():
                    f.write(json.dumps(d_data, ensure_ascii=False) + "\n")
            temp_doc_file.replace(doc_file)

            # Load existing chunks, replace chunks for updated scheme IDs
            updated_scheme_ids = {d.id for d in new_or_updated_docs}
            retained_chunks: List[Dict[str, Any]] = []
            if chunk_file.exists():
                try:
                    with open(chunk_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                c = json.loads(line)
                                if c.get("scheme_id") not in updated_scheme_ids:
                                    retained_chunks.append(c)
                except Exception as err:
                    logger.warning("Could not read existing chunk_file %s: %s", chunk_file, err)

            for c in new_or_updated_chunks:
                retained_chunks.append(c.model_dump())

            # Rewrite chunks.jsonl atomically
            temp_chunk_file = out_base / "chunks.jsonl.tmp"
            with open(temp_chunk_file, "w", encoding="utf-8") as f:
                for c_data in retained_chunks:
                    f.write(json.dumps(c_data, ensure_ascii=False) + "\n")
            temp_chunk_file.replace(chunk_file)

            manifest["documents"] = doc_registry
            manifest["last_ingested_at"] = datetime.now(timezone.utc).isoformat()
            manifest["total_documents"] = len(doc_registry)
            self.save_manifest(manifest_file, manifest)

            result.output_files = [str(doc_file), str(chunk_file), str(manifest_file)]

        return result
