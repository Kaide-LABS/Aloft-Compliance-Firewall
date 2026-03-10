import pytest


@pytest.fixture(autouse=True)
def mock_api_keys(monkeypatch):
    """Set mock API keys for all tests so LLM clients don't fail on import."""
    monkeypatch.setenv("OPENAI_API_KEY", "mock_openai_key")
    monkeypatch.setenv("GOOGLE_API_KEY", "mock_google_key")
    monkeypatch.setenv("EPC_API_KEY", "mock_epc_key")
    monkeypatch.setenv("EPC_API_EMAIL", "mock@test.com")
    monkeypatch.setenv("COMPANIES_HOUSE_API_KEY", "mock_ch_key")


MOCK_EPC_RESPONSE = {
    "rows": [
        {
            "address": "1 Mock St",
            "postcode": "SW1A 2AA",
            "current-energy-rating": "D",
            "potential-energy-rating": "C",
            "property-type": "House",
            "lodgement-date": "2022-01-01",
            "certificate-hash": "mock123",
        }
    ]
}

MOCK_COMPANY_SEARCH_RESPONSE = {
    "items": [
        {
            "company_name": "Foxtons",
            "company_number": "12345678",
            "company_status": "active",
            "date_of_creation": "2020-01-01",
            "registered_office_address": {},
            "type": "ltd",
        }
    ]
}

MOCK_COMPANY_PROFILE_RESPONSE = {
    "company_name": "Mock Co",
    "company_number": "12345678",
    "company_status": "active",
    "date_of_creation": "2020-01-01",
    "registered_office_address": {},
    "type": "ltd",
}

MOCK_LEGISLATION_XML = """<Legislation xmlns="http://www.legislation.gov.uk/namespaces/legislation">
<Primary><Body>
<P1group id="section-1">
  <Title>Minimum energy efficiency standards</Title>
  <P1><P1para><Text>A property must have a minimum EPC rating of E to be legally let in England and Wales.</Text></P1para></P1>
</P1group>
<P1group id="section-2">
  <Title>Penalties for non-compliance</Title>
  <P1><P1para><Text>Landlords who let properties below the minimum standard face fines of up to 30000 pounds.</Text></P1para></P1>
</P1group>
</Body></Primary>
</Legislation>"""
