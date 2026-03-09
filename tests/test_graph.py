import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_full_graph_execution():
    """Test the full graph runs end-to-end with mocked dependencies."""
    from src.agents.legal_rules import LegalRequirementsOutput

    legal_response = LegalRequirementsOutput(
        requirements=[
            {
                "requirement": "Minimum EPC E",
                "legislation": "Energy Efficiency Regulations 2015",
                "section": "Reg 23",
                "source_url": "https://legislation.gov.uk",
            }
        ]
    )

    from src.agents.risk_scorer import RiskAssessment

    risk_response = RiskAssessment(
        risk_score=15, risk_level="GREEN", violations=[], warnings=[]
    )

    summary_response = MagicMock()
    summary_response.content = "This property is fully compliant and clear to lease."

    mock_epc_cert = MagicMock(
        current_energy_rating="C",
        potential_energy_rating="B",
        lodgement_date="2023-06-01",
        address="1 Test St",
        property_type="House",
    )

    with (
        patch("src.agents.legal_rules.structured_llm") as mock_legal_llm,
        patch("src.agents.legal_rules.query_legislation") as mock_rag,
        patch("src.agents.risk_scorer.structured_llm") as mock_risk_llm,
        patch("src.agents.orchestrator.llm") as mock_orch_llm,
        patch("src.agents.property_audit.EPCClient") as mock_epc_cls,
        patch("src.agents.property_audit.get_config") as mock_config,
    ):
        mock_legal_llm.ainvoke = AsyncMock(return_value=legal_response)
        mock_rag.return_value = [
            {
                "content": "test",
                "metadata": {"act_name": "Test Act", "section_title": "S1"},
                "relevance_score": 0.9,
            }
        ]
        mock_risk_llm.ainvoke = AsyncMock(return_value=risk_response)
        mock_orch_llm.ainvoke = AsyncMock(return_value=summary_response)
        mock_config.return_value = MagicMock(
            epc_api_key="test", companies_house_api_key="test"
        )

        mock_epc = AsyncMock()
        mock_epc.search_by_postcode.return_value = [mock_epc_cert]
        mock_epc.get_latest_certificate = MagicMock(return_value=mock_epc_cert)
        mock_epc_cls.return_value = mock_epc

        from src.agents.graph import build_compliance_graph

        graph = build_compliance_graph()

        result = await graph.ainvoke(
            {
                "postcode": "SW1A 2AA",
                "company_name": "",
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

        assert result["risk_level"] == "GREEN"
        assert result["risk_score"] == 15
        assert "compliant" in result["summary"].lower()
        assert len(result["raw_agent_outputs"]) >= 2
