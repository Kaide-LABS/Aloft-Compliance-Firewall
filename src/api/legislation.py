import re
import httpx
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential

# legislation.gov.uk XML namespace
NS = {"leg": "http://www.legislation.gov.uk/namespaces/legislation"}


class LegislationFetcher:
    BASE_URL = "https://www.legislation.gov.uk"

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_legislation_xml(
        self, leg_type: str, year: int, number: int, section: str | None = None
    ) -> str:
        """Fetch legislation as XML text."""
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

    def _extract_text(self, element: ET.Element) -> str:
        """Recursively extract all text from an element, cleaning whitespace."""
        text = "".join(element.itertext()).strip()
        return re.sub(r"\s+", " ", text)

    def _find_title(self, element: ET.Element) -> str:
        """Find the title of a section/paragraph element."""
        for tag in ["Title", "Pnumber"]:
            title_el = element.find(f"leg:{tag}", NS)
            if title_el is not None:
                return self._extract_text(title_el)
        return ""

    def extract_sections_from_xml(self, xml_text: str) -> list[dict]:
        """Parse legislation XML and extract individual sections with metadata."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            return [{"section_number": "error", "title": "Parse error", "text": str(e)}]

        sections = []

        # Try multiple element types that represent discrete sections in UK legislation XML
        section_tags = [
            ".//leg:P1group",
            ".//leg:Section",
            ".//leg:Regulation",
            ".//leg:Article",
            ".//leg:Rule",
        ]

        found_elements: list[ET.Element] = []
        seen_texts: set[str] = set()

        for tag in section_tags:
            for el in root.findall(tag, NS):
                text = self._extract_text(el)
                # Deduplicate — nested structures can cause repeats
                if text and text not in seen_texts and len(text) > 20:
                    seen_texts.add(text)
                    found_elements.append(el)

        if found_elements:
            for i, el in enumerate(found_elements, 1):
                title = self._find_title(el)
                text = self._extract_text(el)
                section_num = el.get("id", f"section-{i}")

                sections.append({
                    "section_number": section_num,
                    "title": title or f"Section {i}",
                    "text": text,
                })
        else:
            # Fallback: if no structured sections found, try P1 elements
            for i, el in enumerate(root.findall(".//leg:P1", NS), 1):
                text = self._extract_text(el)
                if text and len(text) > 20:
                    sections.append({
                        "section_number": el.get("id", f"p1-{i}"),
                        "title": f"Paragraph {i}",
                        "text": text,
                    })

        if not sections:
            # Last resort: extract entire body as one chunk
            body = root.find(".//leg:Body", NS) or root.find(".//leg:Schedule", NS) or root
            full_text = self._extract_text(body)
            if full_text and len(full_text) > 20:
                sections.append({
                    "section_number": "full",
                    "title": "Full text",
                    "text": full_text,
                })

        if not sections:
            sections.append({
                "section_number": "empty",
                "title": "No content extracted",
                "text": "No parseable sections found in this legislation document.",
            })

        return sections
