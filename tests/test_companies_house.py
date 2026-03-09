import pytest
from src.api.companies_house import CompaniesHouseClient


@pytest.mark.asyncio
async def test_search_company_mock():
    client = CompaniesHouseClient(api_key="mock")
    results = await client.search_company("Foxtons")

    assert len(results) == 1
    assert results[0].company_name == "Foxtons"
    assert results[0].company_status == "active"


@pytest.mark.asyncio
async def test_get_company_mock():
    client = CompaniesHouseClient(api_key="mock")
    company = await client.get_company("12345678")

    assert company.company_number == "12345678"
    assert company.company_name == "Mock Co"
