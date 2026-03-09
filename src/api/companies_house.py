import httpx
from src.models.schemas import CompanyProfile


class CompaniesHouseClient:
    BASE_URL = "https://api.company-information.service.gov.uk"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_company(self, name: str) -> list[CompanyProfile]:
        if self.api_key == "mock":
            return [
                CompanyProfile(
                    company_name=name,
                    company_number="12345678",
                    company_status="active",
                    date_of_creation="2020-01-01",
                    registered_office_address={},
                    type="ltd",
                )
            ]

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/companies",
                params={"q": name},
                auth=(self.api_key, ""),
            )
            response.raise_for_status()
            data = response.json()
            return [CompanyProfile(**item) for item in data.get("items", [])]

    async def get_company(self, company_number: str) -> CompanyProfile:
        if self.api_key == "mock":
            return CompanyProfile(
                company_name="Mock Co",
                company_number=company_number,
                company_status="active",
                date_of_creation="2020-01-01",
                registered_office_address={},
                type="ltd",
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/company/{company_number}",
                auth=(self.api_key, ""),
            )
            response.raise_for_status()
            return CompanyProfile(**response.json())
