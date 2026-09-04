#!/usr/bin/env python3
"""CLI script to build FAISS vector store from processed scheme chunks.

Usage:
    python scripts/build_vector_store.py
    python scripts/build_vector_store.py --chunks-file data/processed/chunks.jsonl --output-index vector_store/index.faiss
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.models.document import ProcessedChunk
from app.services.embedding import get_embedding_service
from app.services.vector_store import FAISSVectorStore


def load_chunks(chunks_path: Path) -> List[ProcessedChunk]:
    """Load and validate ProcessedChunk objects from a JSONL file."""
    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Processed chunks file not found: {chunks_path}. "
            f"Run 'python scripts/ingest.py' first."
        )

    chunks: List[ProcessedChunk] = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                chunk = ProcessedChunk.model_validate_json(line)
                chunks.append(chunk)
            except Exception as err:
                print(f"[WARN] Skipping malformed chunk record on line {line_num}: {err}")

    if not chunks:
        raise ValueError(f"No valid chunks found in {chunks_path}.")

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Build FAISS vector store from processed scheme chunks."
    )
    parser.add_argument(
        "--chunks-file",
        type=str,
        default=str(Path(settings.processed_data_dir) / "chunks.jsonl"),
        help="Path to input chunks.jsonl file",
    )
    parser.add_argument(
        "--output-index",
        type=str,
        default=str(settings.resolved_vector_store_path),
        help="Path to output FAISS index file (e.g. vector_store/index.faiss)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Embedding batch size (default: 32)",
    )

    args = parser.parse_args()

    chunks_file = Path(args.chunks_file)
    output_index = Path(args.output_index)

    print("=" * 65)
    print("  AVASAR — Vector Store Index Builder (FAISS)")
    print("=" * 65)
    print(f"  Chunks Source    : {chunks_file}")
    print(f"  Output Index     : {output_index}")
    print(f"  Embedding Model  : {settings.embedding_model}")
    print(f"  Batch Size       : {args.batch_size}")
    print("-" * 65)

    try:
        # 1. Load chunks
        print("--> Loading processed chunks...")
        chunks = load_chunks(chunks_file)
        print(f"    Loaded {len(chunks)} chunks.")

        # 2. Initialize embedding service
        print(f"--> Initializing embedding model ({settings.embedding_model})...")
        t0 = time.time()
        embedding_service = get_embedding_service()
        dimension = embedding_service.dimension
        print(f"    Model ready. Embedding dimension: {dimension}")

        # 3. Generate embeddings
        print(f"--> Generating normalized embeddings for {len(chunks)} chunks...")
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.embed_batch(texts, batch_size=args.batch_size)
        embed_time = time.time() - t0
        print(f"    Embeddings generated in {embed_time:.2f}s (shape: {embeddings.shape})")

        # 4. Create and populate vector store
        print("--> Creating FAISS IndexFlatIP index...")
        store = FAISSVectorStore(dimension=dimension)
        store.add_chunks(chunks=chunks, embeddings=embeddings)

        # 5. Save vector store
        print(f"--> Saving vector store to {output_index}...")
        store.save(output_index)

        print("-" * 65)
        print("  Status           : SUCCESS")
        print(f"  Vectors Indexed  : {store.index.ntotal}")
        print(f"  Vector Dimension : {dimension}")
        print(f"  Index File       : {output_index}")
        print(f"  Metadata File    : {FAISSVectorStore._get_meta_path(output_index)}")
        print("=" * 65)
        return 0

    except Exception as exc:
        print(f"\n[ERROR] Vector store build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
