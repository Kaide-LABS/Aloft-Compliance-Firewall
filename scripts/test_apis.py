"""Quick smoke test — run this to verify all API connections work."""

import asyncio
from dotenv import load_dotenv
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_config
from src.api.epc import EPCClient
from src.api.companies_house import CompaniesHouseClient
from src.api.legislation import LegislationFetcher
from src.rag.store import query_legislation

load_dotenv()


async def main():
    config = get_config()

    # Test 1: EPC API
    print("--- EPC API ---")
    epc = EPCClient(config.epc_api_key)
    certs = await epc.search_by_postcode("SW1A 2AA")
    print(f"Found {len(certs)} certificates for SW1A 2AA")
    if certs:
        latest = epc.get_latest_certificate(certs)
        print(
            f"Latest: Rating {latest.current_energy_rating}, lodged {latest.lodgement_date}"
        )

    # Test 2: Companies House API
    print("\n--- Companies House API ---")
    ch = CompaniesHouseClient(config.companies_house_api_key)
    results = await ch.search_company("Foxtons")
    print(f"Found {len(results)} results for 'Foxtons'")
    if results:
        print(f"First: {results[0].company_name} ({results[0].company_status})")

    # Test 3: Legislation API
    print("\n--- Legislation API ---")
    leg = LegislationFetcher()
    xml = await leg.fetch_legislation_xml("ukpga", 2004, 34, "part/1")
    print(f"Fetched Housing Act 2004 Part 1: {len(xml)} chars of XML")

    # Test 4: RAG Query (only works after ingestion)
    print("\n--- RAG Vector Store ---")
    try:
        results = query_legislation(
            "What is the minimum EPC rating required to let a property?"
        )
        print(f"Found {len(results)} relevant chunks")
        if results:
            print(
                f"Top result from: {results[0]['metadata'].get('act_name')} - {results[0]['metadata'].get('section_title')}"
            )
            print(f"Score: {results[0]['relevance_score']:.3f}")
    except Exception as e:
        print(f"RAG not yet populated (run ingest first): {e}")


if __name__ == "__main__":
    asyncio.run(main())
