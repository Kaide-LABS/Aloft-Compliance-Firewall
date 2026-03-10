import time
from langgraph.graph import StateGraph, START, END
from src.agents.state import ComplianceState
from src.agents.legal_rules import legal_rules_agent
from src.agents.property_audit import property_audit_agent
from src.agents.risk_scorer import risk_scorer_agent
from src.agents.orchestrator import orchestrator_summarize


def timed_agent(name: str, agent_fn):
    """Wrap an agent function with timing."""

    async def wrapper(state):
        start = time.time()
        result = await agent_fn(state)
        elapsed = time.time() - start
        print(f"[{name}] completed in {elapsed:.2f}s")
        return result

    return wrapper


def build_compliance_graph():
    """Build and compile the compliance checking LangGraph."""
    builder = StateGraph(ComplianceState)

    # Add nodes with timing
    builder.add_node("legal_rules", timed_agent("legal_rules", legal_rules_agent))
    builder.add_node(
        "property_audit", timed_agent("property_audit", property_audit_agent)
    )
    builder.add_node("risk_scorer", timed_agent("risk_scorer", risk_scorer_agent))
    builder.add_node("summarize", timed_agent("summarize", orchestrator_summarize))

    # Fan-out: START → legal_rules AND property_audit (parallel)
    builder.add_edge(START, "legal_rules")
    builder.add_edge(START, "property_audit")

    # Fan-in: both converge to risk_scorer
    # LangGraph waits for all incoming edges to complete by default.
    builder.add_edge("legal_rules", "risk_scorer")
    builder.add_edge("property_audit", "risk_scorer")

    # Sequential: risk_scorer → summarize → END
    builder.add_edge("risk_scorer", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()


# Pre-compiled graph instance
compliance_graph = build_compliance_graph()
