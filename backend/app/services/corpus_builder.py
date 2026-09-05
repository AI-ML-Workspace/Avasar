import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from app.core.config import settings
from app.models.document import ProcessedChunk, SchemeDocument
from app.services.chunking import chunk_document
from app.services.ingestion import DocumentIngestionService
from app.services.source_registry import get_source_registry

logger = logging.getLogger(__name__)


@dataclass
class CorpusSummary:
    """Summary of canonical corpus unification run."""
    curated_documents: int = 0
    official_documents: int = 0
    total_documents: int = 0
    duplicates_removed: int = 0
    total_chunks: int = 0
    sources_represented: List[str] = field(default_factory=list)
    output_documents_file: str = ""
    output_chunks_file: str = ""
    output_manifest_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "curated_documents": self.curated_documents,
            "official_documents": self.official_documents,
            "total_documents": self.total_documents,
            "duplicates_removed": self.duplicates_removed,
            "total_chunks": self.total_chunks,
            "sources_represented": self.sources_represented,
            "output_documents_file": self.output_documents_file,
            "output_chunks_file": self.output_chunks_file,
            "output_manifest_file": self.output_manifest_file,
        }


class CorpusBuilderService:
    """Service to construct the unified, canonical government scheme corpus.

    Combines curated static scheme files (data/raw/schemes/) and live-ingested
    official sources (data/ingested/*/), applies deterministic content hashing
    and deduplication, preserves full source provenance, and writes canonical
    documents.jsonl and chunks.jsonl into data/processed/.
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
        self.ingestion_service = DocumentIngestionService(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def discover_curated_documents(self, raw_dir: Union[str, Path]) -> List[SchemeDocument]:
        """Load and normalize curated scheme documents from data/raw/schemes."""
        path = Path(raw_dir)
        if not path.exists():
            logger.warning("Raw directory '%s' does not exist.", path)
            return []
        return self.ingestion_service.load_directory(path)

    def discover_ingested_documents(self, ingested_dir: Union[str, Path]) -> List[SchemeDocument]:
        """Discover and load official documents fetched from registered sources.

        Scans data/ingested/*/schemes.jsonl.
        """
        path = Path(ingested_dir)
        if not path.exists():
            logger.info("Ingested data directory '%s' does not exist yet.", path)
            return []

        official_docs: List[SchemeDocument] = []
        for source_subdir in sorted(path.iterdir()):
            if not source_subdir.is_dir() or source_subdir.name.startswith("."):
                continue

            doc_file = source_subdir / "schemes.jsonl"
            if not doc_file.exists():
                continue

            logger.info("Loading ingested documents from %s", doc_file)
            with open(doc_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        doc = SchemeDocument.model_validate_json(line)
                        official_docs.append(doc)
                    except Exception as err:
                        logger.warning("Skipping invalid JSON in %s line %d: %s", doc_file, line_num, err)

        return official_docs

    def deduplicate_and_merge(
        self,
        curated_docs: List[SchemeDocument],
        official_docs: List[SchemeDocument],
    ) -> (List[SchemeDocument], int):
        """Merge curated and official documents with deterministic deduplication.

        Returns:
            Tuple of (merged_documents, duplicate_count)
        """
        merged: List[SchemeDocument] = []
        seen_ids: Dict[str, SchemeDocument] = {}
        seen_hashes: Dict[str, str] = {}  # content_hash -> doc_id
        duplicates_removed = 0

        # 1. Process curated documents
        for doc in curated_docs:
            chash = doc.content_hash or hashlib.sha256(doc.content.strip().encode("utf-8")).hexdigest()
            doc.content_hash = chash

            if chash in seen_hashes:
                duplicates_removed += 1
                logger.debug("Duplicate content hash '%s' in curated doc '%s', skipping.", chash, doc.id)
                continue

            if doc.id in seen_ids:
                duplicates_removed += 1
                logger.debug("Duplicate doc ID '%s' in curated docs, skipping.", doc.id)
                continue

            seen_hashes[chash] = doc.id
            seen_ids[doc.id] = doc
            merged.append(doc)

        # 2. Additive merge with official ingested documents
        for doc in official_docs:
            chash = doc.content_hash or hashlib.sha256(doc.content.strip().encode("utf-8")).hexdigest()
            doc.content_hash = chash

            if chash in seen_hashes:
                duplicates_removed += 1
                logger.debug("Official doc '%s' has identical content hash to '%s', skipping duplicate.", doc.id, seen_hashes[chash])
                continue

            if doc.id in seen_ids:
                existing = seen_ids[doc.id]
                # If official doc has higher version or newer retrieval, update it
                if doc.version > existing.version or (doc.retrieved_at and not existing.retrieved_at):
                    logger.info("Replacing doc '%s' with newer official version.", doc.id)
                    merged.remove(existing)
                    merged.append(doc)
                    seen_ids[doc.id] = doc
                    seen_hashes[chash] = doc.id
                else:
                    duplicates_removed += 1
                continue

            seen_hashes[chash] = doc.id
            seen_ids[doc.id] = doc
            merged.append(doc)

        return merged, duplicates_removed

    def build_corpus(
        self,
        raw_dir: Optional[Union[str, Path]] = None,
        ingested_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
    ) -> CorpusSummary:
        """Execute the full canonical corpus build pipeline.

        1. Discover curated documents
        2. Discover official-source documents
        3. Deduplicate and merge
        4. Chunk unified documents with preserved provenance
        5. Write canonical documents.jsonl, chunks.jsonl, and corpus_manifest.json
        """
        raw_path = Path(raw_dir) if raw_dir else settings.resolved_raw_data_dir
        ingested_path = Path(ingested_dir) if ingested_dir else settings.resolved_ingestion_data_dir
        out_path = Path(output_dir) if output_dir else settings.resolved_processed_data_dir

        curated_docs = self.discover_curated_documents(raw_path)
        official_docs = self.discover_ingested_documents(ingested_path)

        merged_docs, duplicates_removed = self.deduplicate_and_merge(
            curated_docs=curated_docs,
            official_docs=official_docs,
        )

        all_chunks: List[ProcessedChunk] = []
        sources_set: Set[str] = set()

        for doc in merged_docs:
            if doc.source_id:
                sources_set.add(doc.source_id)
            elif doc.source_name:
                sources_set.add(doc.source_name)

            chunks = chunk_document(
                doc=doc,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            all_chunks.extend(chunks)

        out_docs_file = out_path / "documents.jsonl"
        out_chunks_file = out_path / "chunks.jsonl"
        out_manifest_file = out_path / "corpus_manifest.json"

        summary = CorpusSummary(
            curated_documents=len(curated_docs),
            official_documents=len(official_docs),
            total_documents=len(merged_docs),
            duplicates_removed=duplicates_removed,
            total_chunks=len(all_chunks),
            sources_represented=sorted(sources_set),
            output_documents_file=str(out_docs_file),
            output_chunks_file=str(out_chunks_file),
            output_manifest_file=str(out_manifest_file),
        )

        if not dry_run:
            out_path.mkdir(parents=True, exist_ok=True)

            # 1. Write canonical documents.jsonl (atomic overwrite)
            temp_docs_file = out_path / "documents.jsonl.tmp"
            with open(temp_docs_file, "w", encoding="utf-8") as f:
                for doc in merged_docs:
                    f.write(json.dumps(doc.model_dump(), ensure_ascii=False) + "\n")
            temp_docs_file.replace(out_docs_file)

            # 2. Write canonical chunks.jsonl (atomic overwrite)
            temp_chunks_file = out_path / "chunks.jsonl.tmp"
            with open(temp_chunks_file, "w", encoding="utf-8") as f:
                for chunk in all_chunks:
                    f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")
            temp_chunks_file.replace(out_chunks_file)

            # 3. Write corpus_manifest.json
            manifest_data = summary.to_dict()
            manifest_data["built_at"] = datetime.now(timezone.utc).isoformat()
            manifest_data["chunk_size"] = self.chunk_size
            manifest_data["chunk_overlap"] = self.chunk_overlap

            temp_manifest = out_path / "corpus_manifest.json.tmp"
            with open(temp_manifest, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)
            temp_manifest.replace(out_manifest_file)

            logger.info("Corpus build complete: %d documents, %d chunks saved to %s", len(merged_docs), len(all_chunks), out_path)

        return summary
