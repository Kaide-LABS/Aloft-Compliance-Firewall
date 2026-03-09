import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.companies_house import CompaniesHouseClient
from tests.conftest import MOCK_COMPANY_SEARCH_RESPONSE, MOCK_COMPANY_PROFILE_RESPONSE


@pytest.mark.asyncio
async def test_search_company():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = MOCK_COMPANY_SEARCH_RESPONSE

    with patch("src.api.companies_house.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        client = CompaniesHouseClient(api_key="test-key")
        results = await client.search_company("Foxtons")

        assert len(results) == 1
        assert results[0].company_name == "Foxtons"
        assert results[0].company_status == "active"


@pytest.mark.asyncio
async def test_get_company():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = MOCK_COMPANY_PROFILE_RESPONSE

    with patch("src.api.companies_house.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        client = CompaniesHouseClient(api_key="test-key")
        company = await client.get_company("12345678")

        assert company.company_number == "12345678"
        assert company.company_name == "Mock Co"
