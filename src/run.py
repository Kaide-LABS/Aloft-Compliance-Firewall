import asyncio
import argparse
import json
import sys
import os
from dotenv import load_dotenv

# Add project root to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="Aloft Compliance Firewall")
    parser.add_argument("postcode", help="UK postcode to check")
    parser.add_argument(
        "--company", default="", help="Property management company name to verify"
    )
    args = parser.parse_args()

    from src.agents.graph import compliance_graph

    print(f"\n{'=' * 60}")
    print(f"  COMPLIANCE CHECK: {args.postcode}")
    print(f"{'=' * 60}\n")

    result = await compliance_graph.ainvoke(
        {
            "postcode": args.postcode,
            "company_name": args.company,
            "legal_requirements": [],
            "epc_data": {},
            "company_data": {},
            "risk_score": 0,
            "risk_level": "",
            "violations": [],
            "warnings": [],
            "summary": "",
            "raw_agent_outputs": [],
        }
    )

    # Display results
    level = result.get("risk_level", "UNKNOWN")
    score = result.get("risk_score", 0)

    level_colors = {"GREEN": "✅", "AMBER": "⚠️", "RED": "🚫"}
    icon = level_colors.get(level, "❓")

    print(f"  {icon} VERDICT: {level} (Score: {score}/100)")
    print(f"\n{'─' * 60}")
    print(f"\n{result.get('summary', '')}")

    violations = result.get("violations", [])
    if violations:
        print(f"\n{'─' * 60}")
        print("  VIOLATIONS:")
        for v in violations:
            print(f"    🚫 [{v.get('severity', 'HIGH')}] {v['description']}")
            if v.get("legislation"):
                print(f"       Legislation: {v['legislation']}")

    warnings = result.get("warnings", [])
    if warnings:
        print(f"\n{'─' * 60}")
        print("  WARNINGS:")
        for w in warnings:
            print(f"    ⚠️  {w['description']}")

    print(f"\n{'─' * 60}")
    print(f"  EPC: {json.dumps(result.get('epc_data', {}), indent=4)}")
    print(f"\n{'─' * 60}")
    print(f"  Legal requirements checked: {len(result.get('legal_requirements', []))}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
