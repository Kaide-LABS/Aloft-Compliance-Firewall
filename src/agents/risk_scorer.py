import json
import asyncio
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from src.agents.state import ComplianceState

llm = ChatOpenAI(model="gpt-4o-mini")


class Violation(BaseModel):
    description: str = Field(description="what's wrong")
    severity: Literal["CRITICAL", "HIGH", "MEDIUM"]
    legislation: str = Field(description="which law")


class WarningMsg(BaseModel):
    description: str = Field(description="what to watch")
    expires_in_days: Optional[int] = Field(
        None, description="days until expiration, if any"
    )


class RiskAssessment(BaseModel):
    risk_score: int = Field(description="0-100", ge=0, le=100)
    risk_level: Literal["GREEN", "AMBER", "RED"]
    violations: List[Violation] = Field(default_factory=list)
    warnings: List[WarningMsg] = Field(default_factory=list)


structured_llm = llm.with_structured_output(RiskAssessment)

SYSTEM_PROMPT = """You are a UK property compliance risk assessor. Given:
1. A list of legal requirements that must be satisfied
2. Real property data (EPC rating, company status)

Score the property's compliance risk from 0-100 and classify it:
- GREEN (0-29): Fully compliant, clear to lease
- AMBER (30-69): Minor issues or upcoming expirations, proceed with caution
- RED (70-100): Hard legal violations, DO NOT lease

Scoring rules:
- No EPC on record → RED (score 90). This is itself a compliance violation.
- EPC rating F or G → RED (score 95). Illegal to let since April 2020. Fine up to £30,000.
- EPC rating E with lodgement > 9 years ago → AMBER (score 50). Approaching expiry.
- EPC rating D or above, valid → GREEN contribution.
- Company status "dissolved" or "liquidation" → RED (score 85).
- Company not found → AMBER (score 40). May be sole trader.
- Company status "active" → GREEN contribution.
"""


async def risk_scorer_agent(state: ComplianceState) -> dict:
    epc_data = state.get("epc_data", {})
    company_data = state.get("company_data", {})
    legal_requirements = state.get("legal_requirements", [])

    user_message = f"""Property Data:
- EPC: {json.dumps(epc_data, indent=2)}
- Company: {json.dumps(company_data, indent=2)}

Legal Requirements:
{json.dumps(legal_requirements, indent=2)}

Assess this property's compliance risk."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        response = await asyncio.wait_for(
            structured_llm.ainvoke(messages), timeout=20.0
        )
        result = response.model_dump()
    except asyncio.TimeoutError:
        result = {
            "risk_score": 50,
            "risk_level": "AMBER",
            "violations": [],
            "warnings": [
                {
                    "description": "Risk assessment timed out",
                    "expires_in_days": None,
                }
            ],
        }
    except Exception as e:
        result = {
            "risk_score": 50,
            "risk_level": "AMBER",
            "violations": [],
            "warnings": [
                {
                    "description": f"Risk assessment failed: {str(e)}",
                    "expires_in_days": None,
                }
            ],
        }

    return {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "violations": result.get("violations", []),
        "warnings": result.get("warnings", []),
        "raw_agent_outputs": [{"agent": "risk_scorer", "output": result}],
    }
