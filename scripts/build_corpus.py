#!/usr/bin/env python3
"""CLI tool to build the unified canonical government scheme corpus.

Combines curated scheme files (data/raw/schemes/) and live-ingested official
government sources (data/ingested/*/), applies deterministic content hashing
and deduplication, and generates canonical documents.jsonl and chunks.jsonl.

Usage:
    python scripts/build_corpus.py
    python scripts/build_corpus.py --dry-run
    python scripts/build_corpus.py --raw-dir data/raw/schemes --ingested-dir data/ingested --output-dir data/processed
"""

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.corpus_builder import CorpusBuilderService


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build unified canonical government scheme corpus with full provenance."
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(settings.resolved_raw_data_dir),
        help=f"Path to raw curated scheme directory (default: {settings.resolved_raw_data_dir})",
    )
    parser.add_argument(
        "--ingested-dir",
        type=str,
        default=str(settings.resolved_ingestion_data_dir),
        help=f"Path to official source ingestion directory (default: {settings.resolved_ingestion_data_dir})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(settings.resolved_processed_data_dir),
        help=f"Path to processed corpus destination directory (default: {settings.resolved_processed_data_dir})",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.chunk_size,
        help=f"Chunk size in characters (default: {settings.chunk_size})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.chunk_overlap,
        help=f"Chunk overlap in characters (default: {settings.chunk_overlap})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery, normalization, and deduplication without writing files.",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("  AVASAR — Unified Canonical Corpus Builder")
    print("=" * 65)
    print(f"  Curated Schemes Dir : {args.raw_dir}")
    print(f"  Ingested Sources Dir: {args.ingested_dir}")
    print(f"  Output Corpus Dir   : {args.output_dir}")
    print(f"  Chunk Size / Overlap: {args.chunk_size} / {args.chunk_overlap} chars")
    print(f"  Dry Run             : {args.dry_run}")
    print("-" * 65)

    try:
        builder = CorpusBuilderService(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        summary = builder.build_corpus(
            raw_dir=args.raw_dir,
            ingested_dir=args.ingested_dir,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
        )

        print("\nCorpus Build Summary")
        print("--------------------")
        print(f"Curated documents: {summary.curated_documents}")
        print(f"Official-source documents: {summary.official_documents}")
        print(f"Total documents: {summary.total_documents}")
        print(f"Duplicate documents removed: {summary.duplicates_removed}")
        print(f"Total chunks: {summary.total_chunks}")
        print(f"Sources represented: {len(summary.sources_represented)} ({', '.join(summary.sources_represented)})")
        if not args.dry_run:
            print("Output files:")
            print(f"  * {summary.output_documents_file}")
            print(f"  * {summary.output_chunks_file}")
            print(f"  * {summary.output_manifest_file}")
        print("=" * 65)
        print("Corpus build completed successfully.")
        return 0

    except Exception as exc:
        print(f"\n[ERROR] Corpus build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
