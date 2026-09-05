import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.document import ProcessedChunk
from app.models.source import OfficialSource
from app.services.corpus_builder import CorpusBuilderService
from app.services.embedding import get_embedding_service
from app.services.source_adapters import get_adapter_for_source
from app.services.source_adapters.base import IngestionResult, SourceAdapter
from app.services.source_registry import SourceRegistry, get_source_registry
from app.services.vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


class SourceHealthRecord(BaseModel):
    """Health monitoring status for an official government source."""
    source_id: str
    name: str
    base_url: str
    is_accessible: bool = True
    last_sync_status: str = "UNKNOWN"  # SUCCESS, FAILED, NOT_IMPLEMENTED, SKIPPED
    last_http_status: Optional[int] = None
    last_error: Optional[str] = None
    documents_total: int = 0
    documents_changed: int = 0
    documents_unchanged: int = 0
    documents_rejected: int = 0
    chunks_created: int = 0
    last_synced_at: Optional[str] = None


class SourceSyncReport(BaseModel):
    """Execution report for a scheduled or manual source synchronization run."""
    sync_id: str
    started_at: str
    completed_at: str
    dry_run: bool = False
    sources_attempted: int = 0
    sources_succeeded: int = 0
    sources_failed: int = 0
    total_documents_changed: int = 0
    total_documents_unchanged: int = 0
    total_chunks_created: int = 0
    rebuild_needed: bool = False
    corpus_rebuilt: bool = False
    faiss_rebuilt: bool = False
    sources: Dict[str, SourceHealthRecord] = Field(default_factory=dict)


class SourceSyncService:
    """Service to coordinate official source synchronization, health monitoring, and indexing.

    Ensures:
    1. Modular, isolated execution — failure of one source never crashes others.
    2. Zero data loss on temporary network/server failures (retains prior good data).
    3. Freshness detection using SHA-256 content hashes.
    4. Conditional corpus and FAISS rebuilding — avoids unnecessary re-indexing when nothing changed.
    5. Strict 1:1 vector/chunk alignment when rebuilding.
    6. Non-interactive, scheduled-ready operation for Task Scheduler, cron, or CI/CD.
    """

    def __init__(
        self,
        registry: Optional[SourceRegistry] = None,
        health_file: Optional[Union[str, Path]] = None,
        raw_dir: Optional[Union[str, Path]] = None,
        ingested_dir: Optional[Union[str, Path]] = None,
        processed_dir: Optional[Union[str, Path]] = None,
        vector_store_path: Optional[Union[str, Path]] = None,
    ):
        self.registry = registry or get_source_registry()
        self.ingested_dir = Path(ingested_dir) if ingested_dir else settings.resolved_ingestion_data_dir
        self.raw_dir = Path(raw_dir) if raw_dir else settings.resolved_raw_data_dir
        self.processed_dir = Path(processed_dir) if processed_dir else settings.resolved_processed_data_dir
        self.vector_store_path = Path(vector_store_path) if vector_store_path else settings.resolved_vector_store_path

        if health_file:
            self.health_file = Path(health_file)
        else:
            # Default to data/source_health.json alongside ingested/processed
            self.health_file = self.ingested_dir.parent / "source_health.json"

    def load_health(self) -> Dict[str, SourceHealthRecord]:
        """Load persistent source health records from disk."""
        if not self.health_file.exists():
            return {}

        try:
            with open(self.health_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = {}
                for sid, rdata in data.get("sources", {}).items():
                    records[sid] = SourceHealthRecord.model_validate(rdata)
                return records
        except Exception as err:
            logger.warning("Could not read health file at %s: %s", self.health_file, err)
            return {}

    def save_health(self, records: Dict[str, SourceHealthRecord]) -> None:
        """Atomically persist source health records to disk."""
        self.health_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.health_file.with_suffix(".tmp")
        data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "sources": {sid: rec.model_dump() for sid, rec in records.items()},
        }
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.health_file)

    def count_persisted_documents(self, source_id: str) -> int:
        """Count existing valid documents on disk for a given source."""
        doc_file = self.ingested_dir / source_id / "schemes.jsonl"
        if not doc_file.exists():
            return 0
        count = 0
        try:
            with open(doc_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        count += 1
        except Exception as err:
            logger.warning("Error reading %s: %s", doc_file, err)
        return count

    async def sync_source(
        self,
        source_id: str,
        adapter: Optional[SourceAdapter] = None,
        max_docs: Optional[int] = None,
        dry_run: bool = False,
    ) -> Tuple[SourceHealthRecord, IngestionResult]:
        """Synchronize a single official source safely and record health status."""
        source: Optional[OfficialSource] = self.registry.get_source(source_id)
        name = source.name if source else source_id
        base_url = source.base_url if source else ""

        # Existing count before sync
        existing_doc_count = self.count_persisted_documents(source_id)

        if not source:
            err_msg = f"Source '{source_id}' is not registered in Official Source Registry."
            logger.error(err_msg)
            health = SourceHealthRecord(
                source_id=source_id,
                name=name,
                base_url=base_url,
                is_accessible=False,
                last_sync_status="FAILED",
                last_error=err_msg,
                documents_total=existing_doc_count,
                last_synced_at=datetime.now(timezone.utc).isoformat(),
            )
            result = IngestionResult(source_id=source_id, status="FAILED", errors=[err_msg])
            return health, result

        if adapter is None:
            adapter = get_adapter_for_source(source_id, registry=self.registry)

        if not adapter:
            msg = f"No ingestion adapter implemented for source '{source_id}'."
            logger.info(msg)
            health = SourceHealthRecord(
                source_id=source_id,
                name=source.name,
                base_url=source.base_url,
                is_accessible=True,
                last_sync_status="NOT_IMPLEMENTED",
                last_error=None,
                documents_total=existing_doc_count,
                last_synced_at=datetime.now(timezone.utc).isoformat(),
            )
            result = IngestionResult(source_id=source_id, status="NOT_IMPLEMENTED")
            return health, result

        # Run ingestion
        logger.info("Syncing source '%s' (dry_run=%s, max_docs=%s)...", source_id, dry_run, max_docs)
        try:
            result = await adapter.ingest(
                output_dir=self.ingested_dir,
                max_documents=max_docs,
                dry_run=dry_run,
            )
        except Exception as exc:
            logger.exception("Unhandled error syncing source '%s': %s", source_id, exc)
            result = IngestionResult(
                source_id=source_id,
                status="FAILED",
                errors=[str(exc)],
            )

        now_str = datetime.now(timezone.utc).isoformat()
        is_success = (result.status == "SUCCESS")
        
        # Calculate resulting total documents
        if dry_run or not is_success:
            total_docs = existing_doc_count
        else:
            total_docs = self.count_persisted_documents(source_id)

        health = SourceHealthRecord(
            source_id=source_id,
            name=source.name,
            base_url=source.base_url,
            is_accessible=is_success,
            last_sync_status=result.status,
            last_http_status=result.http_status,
            last_error="; ".join(result.errors) if result.errors else None,
            documents_total=total_docs,
            documents_changed=result.documents_changed,
            documents_unchanged=result.documents_unchanged,
            documents_rejected=result.documents_rejected,
            chunks_created=result.chunks_created,
            last_synced_at=now_str,
        )

        return health, result

    async def sync_all(
        self,
        source_ids: Optional[List[str]] = None,
        max_docs: Optional[int] = None,
        dry_run: bool = False,
        force_rebuild: bool = False,
    ) -> SourceSyncReport:
        """Run synchronization across selected or all registered official sources.

        Rebuilds corpus and FAISS only if:
        1. Any source produced changed documents (documents_changed > 0), OR
        2. force_rebuild is True, OR
        3. Corpus files or vector store are missing on disk.
        """
        started_at = datetime.now(timezone.utc).isoformat()
        sync_id = f"sync_{uuid.uuid4().hex[:12]}"

        # Load existing health records to merge
        health_records = self.load_health()

        target_ids = source_ids
        if not target_ids:
            target_ids = [s.source_id for s in self.registry.list_sources(enabled_only=True)]

        report = SourceSyncReport(
            sync_id=sync_id,
            started_at=started_at,
            completed_at="",
            dry_run=dry_run,
            sources_attempted=len(target_ids),
        )

        for sid in target_ids:
            health, result = await self.sync_source(sid, max_docs=max_docs, dry_run=dry_run)
            report.sources[sid] = health
            health_records[sid] = health

            if result.status == "SUCCESS":
                report.sources_succeeded += 1
            elif result.status == "FAILED":
                report.sources_failed += 1

            report.total_documents_changed += result.documents_changed
            report.total_documents_unchanged += result.documents_unchanged
            report.total_chunks_created += result.chunks_created

        # Determine if corpus and FAISS rebuild is necessary
        chunks_file = self.processed_dir / "chunks.jsonl"
        docs_file = self.processed_dir / "documents.jsonl"
        index_missing = not self.vector_store_path.exists()
        corpus_missing = not (chunks_file.exists() and docs_file.exists())

        report.rebuild_needed = (
            force_rebuild
            or (report.total_documents_changed > 0)
            or index_missing
            or corpus_missing
        )

        if not dry_run:
            self.save_health(health_records)

            if report.rebuild_needed:
                logger.info("Triggering corpus and FAISS index rebuild (changed docs: %d, force: %s, missing: %s)...",
                            report.total_documents_changed, force_rebuild, index_missing or corpus_missing)
                self.rebuild_corpus_and_index()
                report.corpus_rebuilt = True
                report.faiss_rebuilt = True
            else:
                logger.info("No documents changed and index is intact. Skipping corpus and FAISS rebuild.")

        report.completed_at = datetime.now(timezone.utc).isoformat()
        return report

    def rebuild_corpus_and_index(self) -> None:
        """Rebuild canonical corpus and FAISS index with strict 1:1 integrity."""
        # 1. Build canonical corpus
        builder = CorpusBuilderService()
        corpus_summary = builder.build_corpus(
            raw_dir=self.raw_dir,
            ingested_dir=self.ingested_dir,
            output_dir=self.processed_dir,
            dry_run=False,
        )

        chunks_path = self.processed_dir / "chunks.jsonl"
        if not chunks_path.exists():
            raise FileNotFoundError(f"Processed chunks not found at {chunks_path}")

        # 2. Load canonical chunks
        chunks: List[ProcessedChunk] = []
        with open(chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(ProcessedChunk.model_validate_json(line))

        if not chunks:
            raise ValueError(f"No chunks found in canonical corpus: {chunks_path}")

        # 3. Generate embeddings & index to FAISS
        embedding_service = get_embedding_service()
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.embed_batch(texts, batch_size=32)

        store = FAISSVectorStore(dimension=embedding_service.dimension)
        store.add_chunks(chunks=chunks, embeddings=embeddings)
        self.vector_store_path.parent.mkdir(parents=True, exist_ok=True)
        store.save(self.vector_store_path)

        # 4. Strict 1:1 validation
        if store.index.ntotal != len(chunks):
            raise RuntimeError(
                f"FAISS vector count ({store.index.ntotal}) does not match chunk count ({len(chunks)})!"
            )
        logger.info("Successfully rebuilt FAISS vector index with %d vectors.", store.index.ntotal)
