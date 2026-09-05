#!/usr/bin/env python3
"""CLI tool for scheduled synchronization of verified Indian government sources.

Coordinates multi-source ingestion, health telemetry tracking, SHA-256 freshness
detection, and conditional FAISS index rebuilding with 1:1 vector integrity.

Designed to be executed non-interactively from Windows Task Scheduler, cron,
or CI/CD automation pipelines.

Usage:
    python scripts/sync_sources.py --source nsp
    python scripts/sync_sources.py --all
    python scripts/sync_sources.py --all --dry-run
    python scripts/sync_sources.py --all --force-rebuild
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.source_sync import SourceSyncService, SourceSyncReport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sync_sources")


def print_banner(args) -> None:
    print("=" * 70)
    print("  AVASAR — Official Government Source Synchronizer")
    print("=" * 70)
    print(f"  Target Source(s)   : {'ALL registered enabled sources' if args.all else args.source}")
    print(f"  Dry Run            : {args.dry_run}")
    print(f"  Force Rebuild      : {args.force_rebuild}")
    print(f"  Max Docs Per Source: {args.max_docs}")
    if args.health_file:
        print(f"  Health File        : {args.health_file}")
    print("=" * 70)


def print_report(report: SourceSyncReport) -> None:
    print("\n" + "=" * 70)
    print(f"  SYNCHRONIZATION REPORT — ID: {report.sync_id}")
    print("=" * 70)
    print(f"  Execution Window   : {report.started_at} -> {report.completed_at}")
    print(f"  Dry Run Mode       : {report.dry_run}")
    print(f"  Sources Attempted  : {report.sources_attempted}")
    print(f"  Sources Succeeded  : {report.sources_succeeded}")
    print(f"  Sources Failed     : {report.sources_failed}")
    print(f"  Documents Changed  : {report.total_documents_changed}")
    print(f"  Documents Unchanged: {report.total_documents_unchanged}")
    print(f"  Chunks Created     : {report.total_chunks_created}")
    print(f"  Corpus Rebuilt     : {report.corpus_rebuilt}")
    print(f"  FAISS Rebuilt      : {report.faiss_rebuilt}")
    print("-" * 70)
    print("  PER-SOURCE HEALTH & INGESTION TELEMETRY:")
    print("-" * 70)

    for sid, h in sorted(report.sources.items()):
        status_indicator = "[OK]" if h.is_accessible and h.last_sync_status == "SUCCESS" else (
            "[SKIP]" if h.last_sync_status in ("NOT_IMPLEMENTED", "SKIPPED") else "[FAIL]"
        )
        http_code = f"HTTP {h.last_http_status}" if h.last_http_status else "No HTTP response"
        print(f"  {status_indicator} {sid:<14} | Status: {h.last_sync_status:<15} | {http_code}")
        print(f"       Name          : {h.name}")
        print(f"       Total Docs    : {h.documents_total} | Changed: {h.documents_changed} | Unchanged: {h.documents_unchanged}")
        if h.last_error:
            print(f"       Error         : {h.last_error}")
        print(f"       Last Synced   : {h.last_synced_at}")
        print()

    print("=" * 70)


async def main_async() -> int:
    parser = argparse.ArgumentParser(
        description="Scheduled synchronization tool for official Indian government knowledge sources."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--source",
        type=str,
        help="Specific source identifier to synchronize (e.g. nsp, pm_kisan, pmay_urban, pm_mudra).",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Synchronize all registered, enabled official government sources.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and validate sources without writing files to disk or rebuilding index.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild canonical corpus and FAISS vector index even if no documents changed.",
    )
    parser.add_argument(
        "--max-docs",
        type=int,
        default=settings.ingestion_max_documents,
        help=f"Maximum documents to ingest per source (default: {settings.ingestion_max_documents}).",
    )
    parser.add_argument(
        "--health-file",
        type=str,
        default=None,
        help="Custom destination for source health JSON file (default: data/source_health.json).",
    )
    parser.add_argument(
        "--ingested-dir",
        type=str,
        default=None,
        help=f"Custom directory for ingested data (default: {settings.resolved_ingestion_data_dir}).",
    )
    parser.add_argument(
        "--processed-dir",
        type=str,
        default=None,
        help=f"Custom directory for processed corpus (default: {settings.resolved_processed_data_dir}).",
    )

    args = parser.parse_args()
    print_banner(args)

    sync_service = SourceSyncService(
        health_file=args.health_file,
        ingested_dir=args.ingested_dir,
        processed_dir=args.processed_dir,
    )

    source_ids = None if args.all else [args.source.strip().lower()]

    try:
        report = await sync_service.sync_all(
            source_ids=source_ids,
            max_docs=args.max_docs,
            dry_run=args.dry_run,
            force_rebuild=args.force_rebuild,
        )
        print_report(report)

        # In scheduled mode: if a specific source was requested and failed, return 1
        if not args.all and report.sources_failed > 0:
            return 1

        return 0

    except Exception as exc:
        logger.exception("Synchronization run encountered fatal error: %s", exc)
        print(f"\n[FATAL ERROR] {exc}", file=sys.stderr)
        return 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
