"""Run all demo scenarios and verify expected outcomes."""

import asyncio
import time
import os
import sys

# Ensure src module is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from src.agents.graph import compliance_graph  # noqa: E402
from src.demo_postcodes import DEMO_POSTCODES  # noqa: E402

load_dotenv()


async def run_demo_test():
    results = {}
    for scenario, config in DEMO_POSTCODES.items():
        if not config["postcode"]:
            print(f"⏭️  {scenario}: No postcode configured yet — skipping")
            continue

        print(f"\n{'=' * 60}")
        print(f"Testing {scenario} scenario: {config['postcode']}")
        print(f"{'=' * 60}")

        start = time.time()
        result = await compliance_graph.ainvoke(
            {
                "postcode": config["postcode"],
                "company_name": config.get("company", ""),
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
        elapsed = time.time() - start

        level = result.get("risk_level", "UNKNOWN")
        score = result.get("risk_score", 0)
        violations = result.get("violations", [])
        warnings = result.get("warnings", [])

        print(f"  Verdict: {level} (score: {score})")
        print(f"  Violations: {len(violations)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  Time: {elapsed:.1f}s")

        match = level == scenario
        print(f"  Expected {scenario}: {'✅ PASS' if match else '❌ FAIL'}")

        results[scenario] = {
            "passed": match,
            "level": level,
            "score": score,
            "time": elapsed,
        }

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for scenario, r in results.items():
        status = "✅" if r["passed"] else "❌"
        print(
            f"  {status} {scenario}: {r['level']} ({r['score']}/100) in {r['time']:.1f}s"
        )


if __name__ == "__main__":
    asyncio.run(run_demo_test())
