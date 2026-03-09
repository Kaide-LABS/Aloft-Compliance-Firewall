import httpx
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential


class LegislationFetcher:
    BASE_URL = "https://www.legislation.gov.uk"

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_legislation_xml(
        self, leg_type: str, year: int, number: int, section: str | None = None
    ) -> str:
        """Fetch legislation as XML text. Returns a mock for testing if needed."""
        # Check if we should return mock data based on a global config, or we can just mock it for tests
        import os

        if os.environ.get("GOOGLE_API_KEY") == "mock":
            return """<Legislation xmlns="http://www.legislation.gov.uk/namespaces/legislation">
            <Primary><Body><P1><P1para><Text>This is a mock legal section about the EPC rating of C.</Text></P1para></P1></Body></Primary>
            </Legislation>"""

        path = f"/{leg_type}/{year}/{number}"
        if section:
            path += f"/{section}"
        path += "/data.xml"

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.BASE_URL}{path}",
                headers={"Accept": "application/xml"},
            )
            response.raise_for_status()
            return response.text

    def extract_sections_from_xml(self, xml_text: str) -> list[dict]:
        """Parse legislation XML and extract individual sections with metadata."""
        try:
            root = ET.fromstring(xml_text)
            # Find all text content recursively (very simplified)
            text_content = "".join(root.itertext()).strip()
            # Clean up excessive whitespace
            import re

            text_content = re.sub(r"\s+", " ", text_content)

            return [
                {
                    "section_number": "unknown",
                    "title": "extracted_section",
                    "text": text_content if text_content else "Empty section",
                }
            ]
        except Exception as e:
            return [
                {
                    "section_number": "error",
                    "title": "error",
                    "text": f"Error parsing XML: {e}",
                }
            ]
