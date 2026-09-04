import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.core.config import settings
from app.models.document import ProcessedChunk, SchemeDocument
from app.services.chunking import chunk_document

logger = logging.getLogger(__name__)


def _generate_slug(text: str) -> str:
    """Generate a clean slug identifier from a title string."""
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "_", slug)[:64]


def _format_section_value(val: Any) -> str:
    """Format section values whether they are strings, lists, or primitives."""
    if isinstance(val, str):
        return val.strip()
    elif isinstance(val, list):
        items = [f"- {str(item).strip()}" for item in val if str(item).strip()]
        return "\n".join(items)
    return str(val).strip()


class DocumentIngestionService:
    """Ingestion pipeline for government scheme documents.

    Reads raw documents (.json, .jsonl, .txt, .md) from data/raw/,
    normalizes their contents and metadata, splits them into retrieval chunks,
    and writes them into data/processed/ in JSONL format.
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        self.chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
        self.chunk_overlap = (
            chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
        )

    def normalize_scheme_dict(self, data: Dict[str, Any], fallback_id: str) -> SchemeDocument:
        """Convert a raw dictionary into a validated SchemeDocument."""
        title = (
            data.get("title")
            or data.get("scheme_name")
            or data.get("name")
            or fallback_id
        ).strip()

        doc_id = str(data.get("id") or data.get("scheme_id") or _generate_slug(title))
        url = (
            data.get("url")
            or data.get("link")
            or data.get("official_url")
            or data.get("official_source_url")
        )
        source_name = (
            data.get("source_name")
            or data.get("ministry")
            or data.get("department")
            or data.get("provider")
            or data.get("official_source")
            or "Government of India"
        )
        language = data.get("language") or "en"

        # Content extraction: check direct content, or assemble from scheme sections
        content_parts: List[str] = []
        if "content" in data and isinstance(data["content"], str) and data["content"].strip():
            content_parts.append(data["content"].strip())
        else:
            # Common government scheme schema sections
            if data.get("description"):
                content_parts.append(f"{_format_section_value(data['description'])}")
            if data.get("eligibility"):
                content_parts.append(f"Eligibility:\n{_format_section_value(data['eligibility'])}")
            if data.get("benefits"):
                content_parts.append(f"Benefits:\n{_format_section_value(data['benefits'])}")
            if data.get("application_process") or data.get("how_to_apply"):
                proc = data.get("application_process") or data.get("how_to_apply")
                content_parts.append(f"Application Process:\n{_format_section_value(proc)}")
            if data.get("documents_required"):
                content_parts.append(f"Documents Required:\n{_format_section_value(data['documents_required'])}")
            if data.get("important_conditions"):
                content_parts.append(f"Important Conditions:\n{_format_section_value(data['important_conditions'])}")

        full_content = "\n\n".join(content_parts)
        if not full_content:
            # Fallback to json dump of values if no standard fields match
            full_content = title

        # Preserve extra metadata (excluding primary extracted fields)
        primary_keys = {
            "id", "scheme_id", "title", "scheme_name", "name", "url", "link",
            "official_url", "official_source_url", "source_name", "ministry", "department",
            "provider", "official_source", "language", "content", "description",
            "eligibility", "benefits", "application_process", "how_to_apply",
            "documents_required", "important_conditions"
        }
        preserved_metadata = {k: v for k, v in data.items() if k not in primary_keys}

        return SchemeDocument(
            id=doc_id,
            title=title,
            url=url,
            source_name=source_name,
            language=language,
            content=full_content,
            metadata=preserved_metadata,
        )

    def load_file(self, file_path: Union[str, Path]) -> List[SchemeDocument]:
        """Load and normalize documents from a single file.

        Supports .json, .jsonl, .txt, and .md files.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        documents: List[SchemeDocument] = []
        suffix = path.suffix.lower()

        if suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)

            if isinstance(content, list):
                for idx, item in enumerate(content):
                    if isinstance(item, dict):
                        documents.append(
                            self.normalize_scheme_dict(item, fallback_id=f"{path.stem}_{idx}")
                        )
            elif isinstance(content, dict):
                # Check if it wraps a list like {"schemes": [...]}
                nested_list = (
                    content.get("schemes")
                    or content.get("data")
                    or content.get("items")
                )
                if isinstance(nested_list, list):
                    for idx, item in enumerate(nested_list):
                        if isinstance(item, dict):
                            documents.append(
                                self.normalize_scheme_dict(item, fallback_id=f"{path.stem}_{idx}")
                            )
                else:
                    documents.append(self.normalize_scheme_dict(content, fallback_id=path.stem))

        elif suffix == ".jsonl":
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict):
                            documents.append(
                                self.normalize_scheme_dict(item, fallback_id=f"{path.stem}_{line_num}")
                            )
                    except json.JSONDecodeError as err:
                        logger.warning("Skipping invalid JSON line %d in %s: %s", line_num, path.name, err)

        elif suffix in (".txt", ".md"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if text:
                # Extract first heading or fallback to file stem
                first_line = text.split("\n", 1)[0].strip("# ").strip()
                title = first_line if first_line else path.stem
                documents.append(
                    SchemeDocument(
                        id=path.stem,
                        title=title,
                        url=None,
                        source_name="Government of India",
                        language="en",
                        content=text,
                        metadata={"filename": path.name},
                    )
                )

        return documents

    def load_directory(self, raw_dir: Union[str, Path]) -> List[SchemeDocument]:
        """Scan a directory and load all supported scheme documents."""
        directory = Path(raw_dir)
        if not directory.exists():
            raise FileNotFoundError(f"Raw data directory not found: {directory}")

        # If data/raw was passed but schemes/ subdirectory exists, prioritize schemes/
        if (directory / "schemes").is_dir() and directory.name == "raw":
            directory = directory / "schemes"

        all_docs: List[SchemeDocument] = []
        supported_patterns = ["*.json", "*.jsonl", "*.txt", "*.md"]

        for pattern in supported_patterns:
            for file_path in sorted(directory.glob(pattern)):
                # Skip hidden/temporary files
                if file_path.name.startswith("."):
                    continue
                try:
                    docs = self.load_file(file_path)
                    all_docs.extend(docs)
                except Exception as err:
                    logger.error("Failed to load %s: %s", file_path, err)
                    raise

        return all_docs

    def process_documents(self, documents: List[SchemeDocument]) -> List[ProcessedChunk]:
        """Chunk a list of documents using the configured chunk size and overlap."""
        all_chunks: List[ProcessedChunk] = []
        for doc in documents:
            chunks = chunk_document(
                doc=doc,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            all_chunks.extend(chunks)
        return all_chunks

    def save_chunks_jsonl(
        self,
        chunks: List[ProcessedChunk],
        output_file: Union[str, Path],
    ) -> int:
        """Write processed chunks to a JSONL file line-by-line."""
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")

        return len(chunks)

    def run(
        self,
        raw_dir: Optional[Union[str, Path]] = None,
        output_file: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Run the full ingestion and chunking pipeline."""
        src_dir = Path(raw_dir) if raw_dir else Path(settings.raw_data_dir)
        dst_file = (
            Path(output_file)
            if output_file
            else Path(settings.processed_data_dir) / "chunks.jsonl"
        )

        documents = self.load_directory(src_dir)
        chunks = self.process_documents(documents)
        saved_count = self.save_chunks_jsonl(chunks, dst_file)

        return {
            "status": "success",
            "raw_dir": str(src_dir),
            "output_file": str(dst_file),
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "chunks_saved": saved_count,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }
