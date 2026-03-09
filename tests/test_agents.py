import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.state import ComplianceState


def make_base_state(**overrides) -> ComplianceState:
    """Create a base state with defaults for testing."""
    state = {
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
    state.update(overrides)
    return state


@pytest.mark.asyncio
async def test_property_audit_agent():
    """Test property audit agent with mocked API clients."""
    mock_epc_certs = [
        MagicMock(
            current_energy_rating="D",
            potential_energy_rating="C",
            lodgement_date="2022-01-01",
            address="1 Test St",
            property_type="House",
        )
    ]

    with (
        patch("src.agents.property_audit.EPCClient") as mock_epc_cls,
        patch("src.agents.property_audit.get_config") as mock_config,
    ):
        mock_config.return_value = MagicMock(
            epc_api_key="test", companies_house_api_key="test"
        )
        mock_epc = AsyncMock()
        mock_epc.search_by_postcode.return_value = mock_epc_certs
        mock_epc.get_latest_certificate = MagicMock(return_value=mock_epc_certs[0])
        mock_epc_cls.return_value = mock_epc

        from src.agents.property_audit import property_audit_agent

        result = await property_audit_agent(make_base_state())

        assert result["epc_data"]["found"] is True
        assert result["epc_data"]["rating"] == "D"


@pytest.mark.asyncio
async def test_risk_scorer_red_for_low_epc():
    """Test that risk scorer returns RED for EPC rating F."""
    from src.agents.risk_scorer import RiskAssessment

    mock_response = RiskAssessment(
        risk_score=95,
        risk_level="RED",
        violations=[
            {
                "description": "EPC below minimum E",
                "severity": "CRITICAL",
                "legislation": "Energy Efficiency Regulations 2015",
            }
        ],
        warnings=[],
    )

    with patch("src.agents.risk_scorer.structured_llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        from src.agents.risk_scorer import risk_scorer_agent

        state = make_base_state(
            epc_data={"found": True, "rating": "F", "lodgement_date": "2023-01-01"},
            legal_requirements=[
                {
                    "requirement": "Minimum EPC E",
                    "legislation": "Energy Efficiency Regulations 2015",
                    "section": "Reg 23",
                    "source_url": "",
                }
            ],
        )
        result = await risk_scorer_agent(state)

        assert result["risk_level"] == "RED"
        assert result["risk_score"] >= 70
        assert len(result["violations"]) > 0
