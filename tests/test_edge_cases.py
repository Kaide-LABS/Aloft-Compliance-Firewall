import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tests.test_agents import make_base_state


@pytest.mark.asyncio
async def test_property_audit_epc_timeout():
    """Verify graceful handling when EPC API times out."""
    with (
        patch("src.agents.property_audit.EPCClient") as mock_epc_cls,
        patch("src.agents.property_audit.get_config") as mock_config,
    ):
        mock_config.return_value = MagicMock(
            epc_api_key="test", companies_house_api_key="test"
        )
        mock_epc = AsyncMock()
        mock_epc.search_by_postcode.side_effect = TimeoutError("EPC API timeout")
        mock_epc_cls.return_value = mock_epc

        from src.agents.property_audit import property_audit_agent

        result = await property_audit_agent(make_base_state())

        assert result["epc_data"]["found"] is False
        assert (
            "timeout" in result["epc_data"]["error"].lower()
            or "error" in result["epc_data"]["error"].lower()
        )


@pytest.mark.asyncio
async def test_orchestrator_fallback_on_llm_failure():
    """Verify orchestrator produces fallback summary when LLM fails."""
    with patch("src.agents.orchestrator.llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API quota exceeded"))

        from src.agents.orchestrator import orchestrator_summarize

        state = make_base_state(
            risk_level="RED", risk_score=95, violations=[{"description": "test"}]
        )
        result = await orchestrator_summarize(state)

        assert "summary" in result
        assert "RED" in result["summary"]
