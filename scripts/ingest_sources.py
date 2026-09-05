#!/usr/bin/env python3
"""CLI tool for official Indian government data ingestion.

Usage:
    python scripts/ingest_sources.py --source pm_kisan
    python scripts/ingest_sources.py --source myscheme
    python scripts/ingest_sources.py --all
    python scripts/ingest_sources.py --source pm_kisan --max-docs 2 --dry-run
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import List

# Ensure backend directory is in sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.models.source import OfficialSource
from app.services.source_adapters import get_adapter_for_source
from app.services.source_registry import get_source_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_sources")


def print_summary(source_id: str, status: str, result=None, message: str = None) -> None:
    """Print formatted summary adhering to ingestion CLI specification."""
    print("-" * 50)
    print(f"Source: {source_id}")
    print(f"Status: {status}")
    if result:
        print(f"Documents fetched: {result.documents_fetched}")
        print(f"Documents changed: {result.documents_changed}")
        print(f"Documents unchanged: {result.documents_unchanged}")
        print(f"Documents rejected: {result.documents_rejected}")
        print(f"Chunks created: {result.chunks_created}")
        print(f"Errors: {len(result.errors)}")
        if result.errors:
            for err in result.errors:
                print(f"  - {err}")
        if result.output_files:
            print("Output files:")
            for out in result.output_files:
                print(f"  * {out}")
    elif message:
        print(f"Details: {message}")
    print("-" * 50)


async def run_ingestion_for_source(
    source_id: str,
    output_dir: Path,
    max_docs: int,
    dry_run: bool,
) -> bool:
    """Run ingestion for a single registered source.

    Returns True if completed successfully, False otherwise.
    """
    registry = get_source_registry()
    source: OfficialSource = registry.get_source(source_id)

    if not source:
        print_summary(source_id, "FAILED", message=f"Source '{source_id}' is not registered in source registry.")
        return False

    adapter = get_adapter_for_source(source_id, registry=registry)
    if not adapter:
        print_summary(source_id, "NOT IMPLEMENTED", message="No ingestion adapter implemented for this source.")
        return True

    logger.info("Executing ingestion adapter for '%s' (dry_run=%s, max_docs=%s)...", source_id, dry_run, max_docs)
    result = await adapter.ingest(
        output_dir=output_dir,
        max_documents=max_docs,
        dry_run=dry_run,
    )

    print_summary(source_id, result.status, result=result)
    return result.status == "SUCCESS"


async def main_async() -> int:
    parser = argparse.ArgumentParser(
        description="Controlled ingestion engine for verified official Indian government sources."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--source",
        type=str,
        help="Source identifier to ingest (e.g. pm_kisan, myscheme, data_gov).",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Attempt ingestion for all registered official sources.",
    )

    parser.add_argument(
        "--max-docs",
        type=int,
        default=settings.ingestion_max_documents,
        help=f"Maximum documents to fetch per source (default: {settings.ingestion_max_documents}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and validate without writing files to disk.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help=f"Custom destination directory (default: {settings.resolved_ingestion_data_dir}).",
    )

    args = parser.parse_args()
    out_dir = Path(args.output_dir) if args.output_dir else settings.resolved_ingestion_data_dir

    registry = get_source_registry()
    print("=" * 65)
    print("  AVASAR — Official Government Data Ingestion Engine")
    print("=" * 65)
    print(f"  Target Destination: {out_dir}")
    print(f"  Max Documents     : {args.max_docs}")
    print(f"  Dry Run           : {args.dry_run}")
    print("=" * 65)

    all_success = True
    if args.all:
        sources = registry.list_sources(enabled_only=True)
        print(f"Found {len(sources)} enabled sources in registry.\n")
        for src in sources:
            ok = await run_ingestion_for_source(
                src.source_id,
                output_dir=out_dir,
                max_docs=args.max_docs,
                dry_run=args.dry_run,
            )
            if not ok and src.source_id == "pm_kisan":
                all_success = False
    else:
        clean_id = args.source.strip().lower()
        ok = await run_ingestion_for_source(
            clean_id,
            output_dir=out_dir,
            max_docs=args.max_docs,
            dry_run=args.dry_run,
        )
        if not ok:
            all_success = False

    return 0 if all_success else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
