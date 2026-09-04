"""Verification script to test FAISS vector store loading and multilingual retrieval."""

import asyncio
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.rag import RAGService
from app.services.vector_store import FAISSVectorStore


async def main():
    print("=" * 65)
    print("  AVASAR — Phase 3 Vector Store & Retrieval Verification")
    print("=" * 65)

    index_file = settings.resolved_vector_store_path
    meta_file = FAISSVectorStore._get_meta_path(index_file)

    print("\n1. Verifying Generated Files:")
    print(f"   - Index exists : {index_file.exists()} ({index_file.stat().st_size:,} bytes)")
    print(f"   - Meta exists  : {meta_file.exists()} ({meta_file.stat().st_size:,} bytes)")

    print("\n2. Loading Vector Store From Disk:")
    store = FAISSVectorStore.load(index_file)
    print(f"   - Vectors in index : {store.index.ntotal}")
    print(f"   - Dimension        : {store.dimension}")
    print(f"   - Chunks in memory : {len(store.chunks)}")

    rag = RAGService(vector_store=store)

    queries = [
        ("English (Agriculture / PM-KISAN)", "What is PM Kisan financial assistance for farmer families?"),
        ("Hindi (Health / AB-PMJAY)", "आयुष्मान भारत योजना में कितना इलाज मुफ्त मिलता है?"),
        ("Hindi (Housing / PMAY-U)", "प्रधानमंत्री आवास योजना शहरी के लिए आवेदन कैसे करें?"),
        ("English (Skill / Vishwakarma)", "What loans and toolkit incentives are provided to artisans under PM Vishwakarma?"),
        ("Hindi (Girl Child / Sukanya Samriddhi)", "सुकन्या समृद्धि योजना में खाता कैसे खुलवाएं और कितना ब्याज मिलता है?"),
        ("English (Sanitation / Swachh Bharat)", "How much financial incentive is given for building a toilet under Swachh Bharat Grameen?"),
        ("Unrelated / Low Relevance", "How to bake chocolate chip cookies in microwave oven?"),
    ]

    for label, query in queries:
        print("\n" + "-" * 65)
        print(f"Query [{label}]: \"{query}\"")
        results = await rag.retrieve(query, top_k=2)
        for i, res in enumerate(results, 1):
            print(f"  Result #{i}:")
            print(f"    Title : {res.title}")
            print(f"    URL   : {res.url}")
            print(f"    Score : {res.score:.4f} (Cosine Similarity)")
            print(f"    Text  : {res.snippet[:130]}...")

    print("\n" + "=" * 65)
    print("Verification Completed Successfully.")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
