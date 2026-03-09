import httpx
from src.models.schemas import CompanyProfile


class CompaniesHouseClient:
    BASE_URL = "https://api.company-information.service.gov.uk"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_company(self, name: str) -> list[CompanyProfile]:
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
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/company/{company_number}",
                auth=(self.api_key, ""),
            )
            response.raise_for_status()
            return CompanyProfile(**response.json())
