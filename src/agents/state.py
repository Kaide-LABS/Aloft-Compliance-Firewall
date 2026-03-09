import operator
from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict


class ComplianceState(TypedDict):
    # Input
    postcode: str
    company_name: str

    # Agent 1 output: legal requirements checklist
    legal_requirements: Annotated[List[Dict[str, Any]], operator.add]

    # Agent 2 output: property data from real APIs
    epc_data: Dict[str, Any]
    company_data: Dict[str, Any]

    # Agent 3 output: risk assessment
    risk_score: int
    risk_level: str
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

    # Orchestrator output
    summary: str
    raw_agent_outputs: Annotated[List[Dict[str, Any]], operator.add]
