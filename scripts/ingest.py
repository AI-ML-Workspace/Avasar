#!/usr/bin/env python3
"""CLI entry point for running the government scheme document ingestion pipeline.

Usage:
    python scripts/ingest.py
    python scripts/ingest.py --chunk-size 600 --chunk-overlap 150
    python scripts/ingest.py --raw-dir data/raw --output data/processed/chunks.jsonl
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path to allow imports from app
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.ingestion import DocumentIngestionService


def main():
    parser = argparse.ArgumentParser(
        description="Ingest and chunk government scheme documents for Avasar RAG pipeline."
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=settings.raw_data_dir,
        help="Path to directory containing raw scheme files (.json, .jsonl, .txt, .md)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path(settings.processed_data_dir) / "chunks.jsonl"),
        help="Output path for processed chunks (.jsonl)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.chunk_size,
        help=f"Maximum chunk size in characters (default: {settings.chunk_size})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.chunk_overlap,
        help=f"Chunk overlap in characters (default: {settings.chunk_overlap})",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("  AVASAR — Government Scheme Document Ingestion Pipeline")
    print("=" * 65)
    print(f"  Raw Directory    : {args.raw_dir}")
    print(f"  Output JSONL     : {args.output}")
    print(f"  Chunk Size       : {args.chunk_size} chars")
    print(f"  Chunk Overlap    : {args.chunk_overlap} chars")
    print("-" * 65)

    try:
        service = DocumentIngestionService(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        result = service.run(
            raw_dir=args.raw_dir,
            output_file=args.output,
        )

        print("  Status           : SUCCESS")
        print(f"  Documents Loaded : {result['documents_loaded']}")
        print(f"  Chunks Created   : {result['chunks_created']}")
        print(f"  Chunks Saved     : {result['chunks_saved']}")
        print(f"  Saved File       : {result['output_file']}")
        print("=" * 65)
        print("Pipeline run completed successfully.")
        return 0

    except Exception as exc:
        print(f"\n[ERROR] Ingestion failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
