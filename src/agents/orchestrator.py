import json
import asyncio
from langchain_openai import ChatOpenAI
from src.agents.state import ComplianceState

llm = ChatOpenAI(model="gpt-4o")

SYSTEM_PROMPT = """You are the final compliance report writer. Given the risk assessment results,
write a clear, professional summary in 3-5 sentences. Include:
1. The overall verdict (GREEN/AMBER/RED) and what it means
2. The key findings (EPC status, company status)
3. Any critical violations that must be resolved before leasing
4. Any warnings to monitor

Be direct, professional, and specific. This summary will be read by property managers."""


async def orchestrator_summarize(state: ComplianceState) -> dict:
    user_message = f"""Compliance Check Results for {state.get("postcode", "Unknown")}:

Risk Level: {state.get("risk_level", "UNKNOWN")}
Risk Score: {state.get("risk_score", "N/A")}/100

EPC Data: {json.dumps(state.get("epc_data", {}), indent=2)}
Company Data: {json.dumps(state.get("company_data", {}), indent=2)}

Violations: {json.dumps(state.get("violations", []), indent=2)}
Warnings: {json.dumps(state.get("warnings", []), indent=2)}

Legal Requirements Checked: {len(state.get("legal_requirements", []))}

Write the final compliance summary."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        response = await asyncio.wait_for(llm.ainvoke(messages), timeout=20.0)
        return {"summary": response.content}
    except Exception as e:
        level = state.get("risk_level", "UNKNOWN")
        score = state.get("risk_score", "N/A")
        violations = state.get("violations", [])
        return {
            "summary": f"Compliance check completed with verdict {level} (score: {score}/100). "
            f"{len(violations)} violation(s) detected. "
            f"Summary generation failed ({type(e).__name__}) — review details below."
        }
