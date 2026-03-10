import httpx
from src.models.schemas import EPCCertificate


class EPCClient:
    BASE_URL = "https://epc.opendatacommunities.org/api/v1/domestic/search"

    def __init__(self, api_key: str, email: str = ""):
        self.api_key = api_key
        self.email = email

    async def search_by_postcode(self, postcode: str) -> list[EPCCertificate]:
        """Search for EPC certificates by postcode."""
        clean_postcode = postcode.replace(" ", "")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.BASE_URL,
                params={"postcode": clean_postcode},
                headers={"Accept": "application/json"},
                auth=(self.email, self.api_key),
            )
            response.raise_for_status()
            if not response.content:
                return []
            data = response.json()
            rows = data.get("rows", [])
            return [EPCCertificate(**row) for row in rows]

    def get_latest_certificate(
        self, certificates: list[EPCCertificate]
    ) -> EPCCertificate | None:
        """Return the most recent EPC certificate by lodgement date."""
        if not certificates:
            return None
        return sorted(certificates, key=lambda c: c.lodgement_date, reverse=True)[0]
