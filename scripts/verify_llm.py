"""Manual verification script for LLM service and grounded response generation.

Performs an optional real call to the configured LLM provider using retrieved scheme context.
Never logs or prints API keys.
"""

import argparse
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
from app.models.chat import SourceItem
from app.services.llm import LLMService
from app.services.llm_providers import get_llm_provider


async def main():
    parser = argparse.ArgumentParser(description="Verify LLM Service Grounded Generation")
    parser.add_argument(
        "--provider",
        choices=["groq", "gemini", "openai"],
        default=None,
        help=f"Provider to test (default from config: {settings.llm_provider})",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="What is the financial assistance provided under PM-KISAN, and who is eligible?",
        help="Query to test",
    )
    args = parser.parse_args()

    target_provider = args.provider or settings.llm_provider

    print("=" * 65)
    print("  AVASAR — Phase 4 LLM Service Grounded Generation Verification")
    print("=" * 65)
    print(f"\n1. Configuration:")
    print(f"   - Selected Provider : {target_provider}")
    if target_provider == "groq":
        print(f"   - Model             : {settings.groq_model}")
    elif target_provider == "gemini":
        print(f"   - Model             : {settings.gemini_model}")
    elif target_provider == "openai":
        print(f"   - Model             : {settings.openai_model}")
    print(f"   - Temperature       : {settings.llm_temperature}")
    print(f"   - Max Tokens        : {settings.llm_max_tokens}")

    # Prepare sample retrieved scheme context
    sample_sources = [
        SourceItem(
            title="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            url="https://pmkisan.gov.in/",
            snippet=(
                "Under the PM-KISAN scheme, all landholding farmer families across the country "
                "are provided financial benefit of Rs. 6000/- per year in three equal installments "
                "of Rs. 2000/- each, every four months. The funds are transferred directly to "
                "the bank accounts of the beneficiaries through Direct Benefit Transfer (DBT)."
            ),
            score=0.92,
        ),
        SourceItem(
            title="PM-KISAN Eligibility & Exclusions",
            url="https://pmkisan.gov.in/exclusions",
            snippet=(
                "All landholding farmer families who have cultivable landholding in their names are "
                "eligible. Excluded categories include institutional landholders, farmer families holding "
                "constitutional posts, serving or retired government officers/employees, and income tax payees."
            ),
            score=0.88,
        ),
    ]

    print("\n2. Retrieved Context Provided to LLM:")
    for i, s in enumerate(sample_sources, 1):
        print(f"   [{i}] {s.title}")
        print(f"       {s.snippet[:110]}...")

    print(f"\n3. Query: \"{args.query}\"")
    print("\n4. Calling LLM Service for Grounded Answer...")

    try:
        provider_instance = get_llm_provider(provider_name=target_provider)
        llm_service = LLMService(provider=provider_instance)

        response = await llm_service.generate_answer(
            query=args.query,
            sources=sample_sources,
        )

        print("\n" + "-" * 65)
        print("  GENERATED GROUNDED ANSWER:")
        print("-" * 65)
        print(response)
        print("-" * 65)
        print(f"\n  Metadata:")
        print(f"  - Provider : {target_provider}")
        print(f"  - Model    : {provider_instance.model}")
        print(f"  - Sources  : {len(sample_sources)} reference(s)")

    except Exception as e:
        print(f"\n[ERROR] LLM generation failed: {type(e).__name__}: {e}")
        print("Tip: Check if the required API key is set in .env / .env.local.")
        sys.exit(1)

    # Test Grounding: query with no relevant context
    print("\n" + "=" * 65)
    print("5. Testing Grounding (Out-of-context query):")
    unrelated_query = "What is the recipe for chocolate chip cookies?"
    print(f"   Query: \"{unrelated_query}\"")

    try:
        response_unrelated = await llm_service.generate_answer(
            query=unrelated_query,
            sources=sample_sources,
        )
        print("\n  Response to Unrelated Query:")
        print(f"  \"{response_unrelated}\"")
        print("=" * 65)
        print("Verification completed successfully.")
        print("=" * 65)
    except Exception as e:
        print(f"\n[ERROR] Unrelated query test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
