# PRD: Aloft Pre-Leasing Compliance Firewall Demo

## Product Overview

A multi-agent AI system that acts as a real-time compliance firewall for UK property leasing. Before a property can be listed or leased, the system runs automated compliance checks against real UK regulatory data sources and returns a PASS/FAIL verdict with a detailed compliance report.

**Purpose:** Demonstrate to Aloft (PropTech AI company) that this system sits *adjacent* to their existing Leasing AI — it doesn't replace it, it protects it from generating legally dangerous outputs. This is a pilot demo to secure a contract.

**Target audience for the demo:** Ibrahim Javed (CEO, ex-BCG) and Muntasir Syed (CTO, ex-GoCardless).

---

## Problem Statement

UK property managers face a regulatory tsunami:

- **Renters' Rights Act 2025** (full force by mid-2026): Abolishes Section 21 no-fault evictions, mandates Decent Homes Standard compliance, introduces Awaab's Law for damp/mould remediation timelines
- **Making Tax Digital (MTD)** April 2026: Digital record-keeping requirements
- **National Landlord Database**: Real-time regulatory visibility into portfolios

If a property management platform's AI leases a non-compliant property, the landlord faces fines up to £30,000 and legal liability. Currently, compliance checks are manual, slow, and error-prone.

**Aloft's gap:** Their Leasing AI handles tenant acquisition brilliantly. But it has no pre-leasing compliance validation layer. This demo fills that gap.

---

## Solution: Multi-Agent Compliance Swarm

### Architecture

```
Input: Property address/postcode
            │
            ▼
    ┌──────────────┐
    │ Orchestrator  │  (GPT-4o)
    │ Agent         │  Routes, merges, final verdict
    └──────┬───────┘
           │ parallel fan-out
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐ ┌──────────┐
│ Agent 1  │ │ Agent 2   │
│ Legal    │ │ Property  │
│ Rules    │ │ Audit     │
│ (Gemini  │ │ (GPT-4o-  │
│  Flash)  │ │  mini)    │
└────┬─────┘ └─────┬────┘
     │              │
     └──────┬───────┘
            ▼
     ┌──────────┐
     │ Agent 3   │
     │ Risk      │
     │ Scorer    │
     │ (GPT-4o-  │
     │  mini)    │
     └─────┬────┘
           │
           ▼
    ┌──────────────┐
    │ Orchestrator  │
    │ Final Verdict │
    │ + Report      │
    └──────────────┘
            │
            ▼
    Output: GREEN / AMBER / RED
    + Compliance Report PDF
```

### Agent Details

#### Orchestrator (GPT-4o)
- **Role:** Receives property lookup request, fans out to Agents 1 & 2 in parallel, waits for both, triggers Agent 3, merges all results into final verdict
- **Input:** Property postcode/address
- **Output:** Structured verdict (GREEN/AMBER/RED) + full compliance report

#### Agent 1: Legal Rules Agent (Gemini 2.5 Flash)
- **Role:** RAG-powered legal lookup. Queries a vector store of UK housing legislation to return the specific compliance checklist applicable to this property type and region
- **Data sources:**
  - legislation.gov.uk REST API (Renters' Rights Act, Housing Act 2004, Energy Efficiency Regulations 2015)
  - GOV.UK Content API (landlord guidance, Decent Homes Standard docs)
- **Input:** Property type, region, tenancy type
- **Output:** Structured JSON checklist of compliance requirements with legislation citations

#### Agent 2: Property Audit Agent (GPT-4o-mini)
- **Role:** Pulls real property data and checks against compliance requirements
- **Data sources:**
  - EPC Open Data API (DLUHC) — real EPC ratings, expiry dates, recommendations
  - Companies House API — verify property management company registration
- **Input:** Property postcode/address
- **Output:** Structured JSON with property status (EPC rating, expiry, company verification, any flags)

#### Agent 3: Risk Scorer (GPT-4o-mini)
- **Role:** Takes outputs from Agents 1 and 2, scores the property 0-100, classifies as GREEN/AMBER/RED
- **Input:** Agent 1 checklist + Agent 2 property status
- **Output:** Risk score (0-100), classification (GREEN/AMBER/RED), list of violations, list of warnings
- **Scoring logic:**
  - RED (70-100): Any hard legal violation (expired/below-minimum EPC, unregistered company, Decent Homes failure)
  - AMBER (30-69): Upcoming expirations (within 30 days), minor documentation gaps
  - GREEN (0-29): Fully compliant, clear to lease

---

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Language | Python 3.12+ | LangGraph ecosystem, fast prototyping |
| Agent orchestration | LangGraph | Multi-provider support, fan-out/merge graph, state management |
| LLM: Orchestrator | OpenAI GPT-4o | Best function calling for routing/merging |
| LLM: Agent 1 | Google Gemini 2.5 Flash (via Vertex AI) | Cheap, fast, large context for legal doc RAG |
| LLM: Agents 2 & 3 | OpenAI GPT-4o-mini | Cheap, precise structured output |
| Embeddings | Google text-embedding-004 (via Vertex AI) | Free tier, high quality |
| Vector store | InMemoryVectorStore | Pure python, zero infrastructure, works on Python 3.13 |
| Frontend | Streamlit | Fast to build, looks professional enough for a demo |
| PDF generation | ReportLab or WeasyPrint | Compliance report output |

---

## Real API Integrations

### 1. EPC Open Data API (DLUHC)
- **Registration:** Instant — accept open data license, get API key
- **Endpoint:** `https://epc.opendatacommunities.org/api/v1/domestic/search`
- **Returns:** EPC rating (A-G), certificate number, expiry date, property type, recommendations
- **Demo value:** Type a real postcode, get real compliance data live

### 2. legislation.gov.uk REST API
- **Registration:** None required — fully open
- **Endpoint:** `https://www.legislation.gov.uk/ukpga/{year}/{chapter}/data.xml`
- **Returns:** Full legislation text in XML/JSON
- **Usage:** Ingest key statutes into InMemoryVectorStore vector store for RAG

### 3. GOV.UK Content API
- **Registration:** None required — fully open
- **Endpoint:** `https://www.gov.uk/api/content/{path}`
- **Returns:** Government guidance documents
- **Usage:** Supplement the legal vector store with practical guidance

### 4. Companies House API
- **Registration:** Instant — create account, get API key immediately
- **Endpoint:** `https://api.company-information.service.gov.uk/`
- **Returns:** Company status, directors, filing history
- **Usage:** Verify property management company is registered and active

---

## Data Pipeline: Legal RAG Vector Store

### Documents to ingest:
1. **Renters' Rights Act 2025** — full text from legislation.gov.uk
2. **Housing Act 2004** — Part 1 (Housing Conditions), Part 2 (Licensing)
3. **Energy Efficiency (Private Rented Property) Regulations 2015** (amended 2023)
4. **Decent Homes Standard** — technical guidance from GOV.UK
5. **Awaab's Law** — specific damp/mould remediation timelines
6. **Section 8 Housing Act 1988** — updated possession grounds

### Chunking strategy:
- Split by section/clause (not arbitrary token counts)
- Each chunk tagged with: act name, section number, topic, effective date
- Metadata enables precise citation in compliance reports

---

## Frontend (Streamlit Dashboard)

### Screen 1: Property Lookup
- Input field: UK postcode or full address
- "Run Compliance Check" button
- Loading state showing which agents are active

### Screen 2: Results Dashboard
- Large GREEN/AMBER/RED badge
- Risk score: 0-100 with visual gauge
- Violations list (if any) with severity tags
- Warnings list (if any) with expiry countdowns
- Expandable sections showing:
  - EPC data pulled live
  - Applicable legislation with citations
  - Company verification status

### Screen 3: Compliance Report
- "Download PDF Report" button
- Professional report with:
  - Property details
  - Compliance status
  - Each check performed with PASS/FAIL
  - Legislative citations for every finding
  - Recommended actions for any failures
  - Timestamp and audit trail

---

## Development Phases

### Phase 1: Foundation & Data Pipeline
**Scope:** Project setup, API integrations, legal RAG vector store
- Initialize Python project with dependency management (uv or poetry)
- Set up LangGraph project structure
- Integrate EPC Open Data API (registration + working client)
- Integrate Companies House API (registration + working client)
- Ingest legislation from legislation.gov.uk into InMemoryVectorStore
- Ingest GOV.UK guidance documents into InMemoryVectorStore
- Verify embeddings and RAG retrieval quality
- **Acceptance criteria:** Can query each API and get real data. Can ask a legal question and get a relevant, cited answer from the vector store.

### Phase 2: Agent Implementation
**Scope:** Build all 4 agents with LangGraph
- Implement Agent 1 (Legal Rules) with Gemini Flash + RAG
- Implement Agent 2 (Property Audit) with GPT-4o-mini + real APIs
- Implement Agent 3 (Risk Scorer) with GPT-4o-mini
- Implement Orchestrator with GPT-4o + fan-out/merge graph
- Wire up the full LangGraph state graph
- Test end-to-end with real postcodes
- **Acceptance criteria:** Input a postcode, get a structured GREEN/AMBER/RED verdict with real data and real legal citations.

### Phase 3: Frontend & Report Generation
**Scope:** Streamlit UI + PDF compliance report
- Build Streamlit dashboard (lookup, results, report screens)
- Implement PDF report generation
- Add loading states and agent activity visualization
- Polish UI for demo presentation
- **Acceptance criteria:** Professional-looking demo that a non-technical founder would be impressed by. PDF report looks like it came from a compliance consultancy.

### Phase 4: Demo Polish & Edge Cases
**Scope:** Hardening for the live demo
- Test with 20+ real UK postcodes across different scenarios (expired EPC, low rating, missing data)
- Handle API errors gracefully (timeouts, missing data, rate limits)
- Add demo script with pre-selected postcodes that showcase GREEN, AMBER, and RED outcomes
- Performance optimization (target <10 second total check time)
- Prepare pitch talking points mapped to each screen
- **Acceptance criteria:** Can run the demo 10 times in a row without failure. Have 3 pre-vetted postcodes that reliably produce GREEN, AMBER, and RED results.

---

## Cost Model (Key Pitch Number)

| Agent | Model | Est. Input Tokens | Est. Output Tokens | Cost per check |
|-------|-------|-------------------|--------------------|--------------------|
| Orchestrator (x2) | GPT-4o | ~2,000 | ~500 | ~$0.01 |
| Agent 1 | Gemini Flash | ~15,000 | ~800 | ~$0.001 |
| Agent 2 | GPT-4o-mini | ~1,500 | ~400 | ~$0.0003 |
| Agent 3 | GPT-4o-mini | ~2,000 | ~300 | ~$0.0003 |
| **Total** | | | | **~$0.012 (~1.2p)** |

**Pitch line:** "Full regulatory compliance assurance for about a penny per property."

---

## Success Criteria for the Demo

1. **Technical:** System runs end-to-end on real data with real APIs, no mock data
2. **Speed:** Full compliance check completes in under 10 seconds
3. **Accuracy:** Correctly identifies known non-compliant properties (expired/low EPC)
4. **Visual:** Dashboard looks professional, PDF report looks institutional-grade
5. **Cost:** Demonstrably cheap — show the API cost logs
6. **Adjacent value:** Clearly positioned as a complement to Aloft's existing AI, not a competitor

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| EPC API rate limits during demo | Cache results for demo postcodes |
| Legislation changes between now and demo | Vector store timestamps all documents; show this as a feature ("always up to date") |
| Property not found in EPC database | Handle gracefully — "No EPC on record" is itself a compliance flag |
| Demo internet connection issues | Pre-cache API responses as fallback |

---

---
---

# PHASE 1 SPEC: Foundation & Data Pipeline

**Status:** Active
**Scope:** Project setup, API integrations, legal RAG vector store
**Goal:** By the end of this phase, we can (1) query EPC and Companies House APIs and get real data, and (2) ask a legal question and get a relevant, cited answer from the vector store.

---

## 1. Project Structure

```
aloft-compliance-firewall/
├── pyproject.toml              # Project config (use uv for package management)
├── .env                        # API keys (DO NOT COMMIT)
├── .env.example                # Template for required env vars
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py               # Load env vars, validate API keys present
│   ├── api/
│   │   ├── __init__.py
│   │   ├── epc.py              # EPC Open Data API client
│   │   ├── companies_house.py  # Companies House API client
│   │   └── legislation.py      # legislation.gov.uk fetcher (for RAG ingestion)
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py           # Legislation ingestion pipeline
│   │   ├── embeddings.py       # Gemini text-embedding-004 wrapper
│   │   ├── store.py            # InMemoryVectorStore collection setup and query
│   │   └── chunks/             # Cached chunked legislation (optional, for debugging)
│   └── models/
│       ├── __init__.py
│       └── schemas.py          # Pydantic models for API responses and compliance data
├── scripts/
│   ├── ingest_legislation.py   # One-time script to populate the vector store
│   └── test_apis.py            # Quick script to verify all API connections work
└── tests/
    ├── __init__.py
    ├── test_epc.py
    ├── test_companies_house.py
    └── test_rag.py
```

## 2. Dependencies

```toml
[project]
name = "aloft-compliance-firewall"
requires-python = ">=3.12"
dependencies = [
    "langchain>=0.3",
    "langchain-google-genai>=2.1",
    "langchain-openai>=0.3",
    "langgraph>=0.4",
    
    "httpx>=0.28",
    "pydantic>=2.10",
    "python-dotenv>=1.1",
    "pydantic-settings>=2.7",
    "tenacity>=9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.25",
    "ruff>=0.9",
]
```

**Package manager:** Use `uv` (fast, modern). Initialize with `uv init` then `uv add <deps>`.

## 3. Environment Variables

```env
# .env.example
EPC_API_KEY=           # Get from https://epc.opendatacommunities.org/ (instant registration)
COMPANIES_HOUSE_API_KEY=  # Get from https://developer.company-information.service.gov.uk/ (instant)
OPENAI_API_KEY=        # For GPT-4o and GPT-4o-mini (Phase 2)
GOOGLE_API_KEY=        # For Gemini Flash + text-embedding-004
```

## 4. API Client: EPC Open Data (`src/api/epc.py`)

### Key Implementation Details (from indexed docs):

- **Base URL:** `https://epc.opendatacommunities.org/api/v1/domestic/search`
- **Auth:** HTTP Basic Authentication — `Authorization: Basic <api-key>` (the API key IS the basic auth token, no encoding of user:pass needed — just use the key directly)
- **Response format:** Set `Accept: application/json` header for JSON responses
- **Search by postcode:** Query param `?postcode=SW1A2AA` (spaces removed)
- **Response fields:** The API returns certificate data including (from the glossary): `current-energy-rating` (A-G), `lodgement-date`, `certificate-hash`, `address`, `property-type`, `total-floor-area`, `expiry-date` among others
- **Pagination:** Results may be paginated — check for pagination headers

### Pydantic Schema (`src/models/schemas.py`):

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional

class EPCCertificate(BaseModel):
    address: str = Field(..., alias="address")
    postcode: str = Field(..., alias="postcode")
    current_energy_rating: str = Field(..., alias="current-energy-rating")
    potential_energy_rating: str = Field(..., alias="potential-energy-rating")
    property_type: str = Field(..., alias="property-type")
    lodgement_date: str = Field(..., alias="lodgement-date")
    certificate_hash: str = Field(..., alias="certificate-hash")
    # Add more fields as needed from API response

    model_config = ConfigDict(populate_by_name=True)

class EPCSearchResult(BaseModel):
    certificates: list[EPCCertificate]
    total_count: int
```

### Client Implementation Pattern:

```python
import httpx
from src.models.schemas import EPCCertificate

class EPCClient:
    BASE_URL = "https://epc.opendatacommunities.org/api/v1/domestic/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_by_postcode(self, postcode: str) -> list[EPCCertificate]:
        """Search for EPC certificates by postcode."""
        # Remove spaces from postcode
        clean_postcode = postcode.replace(" ", "")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.BASE_URL,
                params={"postcode": clean_postcode},
                headers={
                    "Accept": "application/json",
                    auth=(self.api_key, ""), # HTTPX basic auth handles encoding
                },
            )
            response.raise_for_status()
            data = response.json()
            # Parse rows into EPCCertificate models
            rows = data.get("rows", [])
            return [EPCCertificate(**row) for row in rows]

    def get_latest_certificate(self, certificates: list[EPCCertificate]) -> EPCCertificate | None:
        """Return the most recent EPC certificate by lodgement date."""
        if not certificates:
            return None
        return sorted(certificates, key=lambda c: c.lodgement_date, reverse=True)[0]
```

### Compliance Logic (to be used by Agent 2 in Phase 2):
- EPC rating below E → **RED** (illegal to let since April 2020, fines up to £30,000)
- EPC expired (lodgement > 10 years ago) → **RED**
- EPC rating E, expiring within 30 days → **AMBER**
- No EPC on record → **RED** (itself a compliance violation)
- EPC rating D or above, valid → **GREEN**

## 5. API Client: Companies House (`src/api/companies_house.py`)

### Key Implementation Details:

- **Base URL:** `https://api.company-information.service.gov.uk`
- **Auth:** HTTP Basic Authentication — API key as username, empty password. Encode as `base64(api_key + ":")`
- **Search endpoint:** `GET /search/companies?q={company_name}`
- **Company profile:** `GET /company/{company_number}`
- **Response format:** JSON by default

### Pydantic Schema:

```python
class CompanyProfile(BaseModel):
    company_name: str
    company_number: str
    company_status: str          # "active", "dissolved", etc.
    date_of_creation: str
    registered_office_address: dict
    type: str                    # "ltd", "plc", etc.

class CompanySearchResult(BaseModel):
    items: list[CompanyProfile]
    total_results: int
```

### Client Implementation Pattern:

```python
import httpx
import base64

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
```

### Compliance Logic:
- Company status is "dissolved" or "liquidation" → **RED**
- Company status is "active" → **GREEN**
- Company not found → **AMBER** (may be sole trader — flag for manual check)

## 6. Legislation Fetcher (`src/api/legislation.py`)

### Key Implementation Details (from indexed legislation.gov.uk docs):

- **No authentication required** — fully open API
- **Format:** XML only (no JSON available). Use `data.xml` representation URIs
- **URI pattern:** `https://www.legislation.gov.uk/{type}/{year}/{number}/data.xml`
  - For specific sections: append `/{divisionName}/{number}` before `/data.xml`
  - Acts use `section` as division name
  - Example: `https://www.legislation.gov.uk/ukpga/2004/34/part/1/data.xml` (Housing Act 2004, Part 1)

### Legislation to Fetch:

| Legislation | URI Type | Year | Number | Parts to Fetch |
|---|---|---|---|---|
| Housing Act 2004 | `ukpga` | 2004 | 34 | Part 1 (Housing Conditions), Part 2 (Licensing) |
| Energy Efficiency (Private Rented Property) (England and Wales) Regulations 2015 | `uksi` | 2015 | 962 | Full |
| Renters' Rights Act 2025 | `ukpga` | 2025 | TBD | Full (check legislation.gov.uk for exact number) |
| Housing Act 1988 (Section 8 grounds) | `ukpga` | 1988 | 50 | Schedule 2 (grounds for possession) |
| Homes (Fitness for Human Habitation) Act 2018 | `ukpga` | 2018 | 34 | Full |

### Fetcher Pattern:

```python
import httpx
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential

class LegislationFetcher:
    BASE_URL = "https://www.legislation.gov.uk"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_legislation_xml(self, leg_type: str, year: int, number: int, section: str | None = None) -> str:
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

    def extract_sections_from_xml(self, xml_text: str) -> list[dict]:
        """Parse legislation XML and extract individual sections with metadata."""
        # Parse XML, extract section titles, body text, and section numbers
        # Return list of dicts: {"section_number": "...", "title": "...", "text": "...", "act_name": "..."}
        # Use lxml to navigate the Legislation XML schema
        # The XML uses namespaces — handle with nsmap
        root = ET.fromstring(xml_text)
        # Implementation: walk the XML tree, extract <Section> or <P1> elements
        # Each chunk should be a self-contained section suitable for embedding
        ...
```

**Important XML parsing notes:**
- legislation.gov.uk XML uses the namespace `http://www.legislation.gov.uk/namespaces/legislation`
- Sections are typically in `<Section>` or `<P1>` elements
- Section titles are in `<Title>` child elements
- Body text is in `<P1para>`, `<P2>`, `<P3>` etc. nested paragraph elements
- The XML schema is complex — Gemini should inspect a sample response and adapt the parser accordingly

## 7. RAG Pipeline: Vector Store (`src/rag/`)

### Embeddings (`src/rag/embeddings.py`):

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        # Uses GOOGLE_API_KEY from env automatically
    )
```

### InMemoryVectorStore Store (`src/rag/store.py`):

```python
import os
from langchain_community.vectorstores import InMemoryVectorStore
from src.rag.embeddings import get_embedding_model

PERSIST_DIR = "./data/in_memory"

def get_vector_store(create_if_missing: bool = False) -> InMemoryVectorStore:
    embedding = get_embedding_model()
    if os.path.exists(PERSIST_DIR):
        return InMemoryVectorStore.load_local(PERSIST_DIR, embedding, allow_dangerous_deserialization=True)
    elif create_if_missing:
        # Create empty InMemoryVectorStore store
        # requires at least one document to init
        from langchain.docstore.document import Document
        return InMemoryVectorStore.from_documents([Document(page_content="init")], embedding)
    else:
        raise ValueError("InMemoryVectorStore index not found. Run ingest first.")

def save_vector_store(store: InMemoryVectorStore):
    store.save_local(PERSIST_DIR)

def query_legislation(question: str, k: int = 5) -> list[dict]:
    """Query the vector store and return relevant legislation chunks with metadata."""
    
    results = store.similarity_search_with_score(question, k=k)
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,  # act_name, section_number, title, etc.
            "relevance_score": score,
        }
        for doc, score in results
    ]
```

### Ingestion Pipeline (`src/rag/ingest.py`):

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.api.legislation import LegislationFetcher
from src.rag.store import get_vector_store

# Legislation manifest — what to ingest
LEGISLATION_MANIFEST = [
    {"type": "ukpga", "year": 2004, "number": 34, "name": "Housing Act 2004", "sections": ["part/1", "part/2"]},
    {"type": "uksi", "year": 2015, "number": 962, "name": "Energy Efficiency Regulations 2015", "sections": [None]},
    {"type": "ukpga", "year": 1988, "number": 50, "name": "Housing Act 1988", "sections": ["schedule/2"]},
    {"type": "ukpga", "year": 2018, "number": 34, "name": "Homes (Fitness for Human Habitation) Act 2018", "sections": [None]},
    # Add Renters' Rights Act 2025 once act number is confirmed on legislation.gov.uk
]

async def ingest_all_legislation():
    fetcher = LegislationFetcher()
    
    all_documents = []

    for leg in LEGISLATION_MANIFEST:
        for section in leg["sections"]:
            xml_text = await fetcher.fetch_legislation_xml(
                leg["type"], leg["year"], leg["number"], section
            )
            sections = fetcher.extract_sections_from_xml(xml_text)
            for s in sections:
                doc = Document(
                    page_content=s["text"],
                    metadata={
                        "act_name": leg["name"],
                        "section_number": s["section_number"],
                        "section_title": s["title"],
                        "legislation_type": leg["type"],
                        "year": leg["year"],
                        "source_url": f"https://www.legislation.gov.uk/{leg['type']}/{leg['year']}/{leg['number']}/{section or ''}",
                    },
                )
                all_documents.append(doc)

    # Chunk documents that are too long (some sections are very large)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(all_documents)

    # Add to InMemoryVectorStore
    store = get_vector_store(create_if_missing=True)
    store.add_documents(chunks)
    save_vector_store(store)
    print(f"Ingested {len(chunks)} chunks from {len(LEGISLATION_MANIFEST)} pieces of legislation")
```

### Ingestion Script (`scripts/ingest_legislation.py`):

```python
import asyncio
from dotenv import load_dotenv
from src.rag.ingest import ingest_all_legislation

load_dotenv()

if __name__ == "__main__":
    asyncio.run(ingest_all_legislation())
```

## 8. Verification Script (`scripts/test_apis.py`)

```python
"""Quick smoke test — run this to verify all API connections work."""
import asyncio
from dotenv import load_dotenv
from src.config import get_config
from src.api.epc import EPCClient
from src.api.companies_house import CompaniesHouseClient
from src.api.legislation import LegislationFetcher
from src.rag.store import query_legislation

load_dotenv()

async def main():
    config = get_config()

    # Test 1: EPC API
    print("--- EPC API ---")
    epc = EPCClient(config.epc_api_key)
    certs = await epc.search_by_postcode("SW1A 2AA")
    print(f"Found {len(certs)} certificates for SW1A 2AA")
    if certs:
        latest = epc.get_latest_certificate(certs)
        print(f"Latest: Rating {latest.current_energy_rating}, lodged {latest.lodgement_date}")

    # Test 2: Companies House API
    print("\n--- Companies House API ---")
    ch = CompaniesHouseClient(config.companies_house_api_key)
    results = await ch.search_company("Foxtons")
    print(f"Found {len(results)} results for 'Foxtons'")
    if results:
        print(f"First: {results[0].company_name} ({results[0].company_status})")

    # Test 3: Legislation API
    print("\n--- Legislation API ---")
    leg = LegislationFetcher()
    xml = await leg.fetch_legislation_xml("ukpga", 2004, 34, "part/1")
    print(f"Fetched Housing Act 2004 Part 1: {len(xml)} chars of XML")

    # Test 4: RAG Query (only works after ingestion)
    print("\n--- RAG Vector Store ---")
    try:
        results = query_legislation("What is the minimum EPC rating required to let a property?")
        print(f"Found {len(results)} relevant chunks")
        if results:
            print(f"Top result from: {results[0]['metadata'].get('act_name')} - {results[0]['metadata'].get('section_title')}")
            print(f"Score: {results[0]['relevance_score']:.3f}")
    except Exception as e:
        print(f"RAG not yet populated (run ingest first): {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 9. Config (`src/config.py`)

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    epc_api_key: str
    companies_house_api_key: str
    openai_api_key: str
    google_api_key: str

    model_config = ConfigDict(env_file=".env")

# Also add import:
# from pydantic import ConfigDict

def get_config() -> Config:
    return Config()
```

**Note:** Add `pydantic-settings` to dependencies.

## 10. Acceptance Criteria

Phase 1 is DONE when:

- [ ] `uv run python scripts/test_apis.py` passes all 4 tests
- [ ] EPC API returns real certificate data for a UK postcode
- [ ] Companies House API returns real company data
- [ ] legislation.gov.uk XML is fetched and parsed into sections
- [ ] InMemoryVectorStore is populated with legislation chunks (run `scripts/ingest_legislation.py`)
- [ ] RAG query returns relevant, cited legislation for a compliance question
- [ ] All code passes `ruff check` and `ruff format`
- [ ] Tests in `tests/` pass with `uv run pytest`

## 11. Notes for Gemini (Executor)

- **Start with API registrations:** Register for EPC and Companies House API keys first. Both are instant.
- **XML parsing is the hardest part:** The legislation.gov.uk XML schema is complex. Fetch a sample XML response first, inspect it, then build the parser. Don't try to handle every edge case — focus on extracting readable section text with metadata.
- **InMemoryVectorStore persistence:** Use `persist_directory` so the vector store survives between runs. Don't re-ingest every time.
- **Renters' Rights Act 2025:** This may or may not be on legislation.gov.uk yet. If not available, skip it in the manifest and add a TODO. The other acts are sufficient for the demo.
- **Don't over-engineer:** This is Phase 1 — get the data flowing. No error handling beyond basic `raise_for_status()`. No retries. No caching. That comes in Phase 4.

---

---
---

# PHASE 2 SPEC: Agent Implementation

**Status:** Active
**Scope:** Build all 4 LangGraph agents with mixed OpenAI + Gemini models, wire up the full fan-out/merge graph
**Goal:** Input a UK postcode → get a structured GREEN/AMBER/RED verdict with real EPC data, real company verification, and real legal citations.

**Prerequisite:** Phase 1 is complete. All API clients work, RAG vector store is populated with UK housing legislation.

---

## 1. New Files to Create

```
src/
├── agents/
│   ├── __init__.py
│   ├── state.py              # LangGraph state schema
│   ├── orchestrator.py       # Orchestrator node (GPT-4o)
│   ├── legal_rules.py        # Agent 1: Legal rules via RAG (Gemini Flash)
│   ├── property_audit.py     # Agent 2: Property data check (GPT-4o-mini)
│   ├── risk_scorer.py        # Agent 3: Risk scoring (GPT-4o-mini)
│   └── graph.py              # LangGraph graph definition and compilation
├── run.py                    # CLI entry point: python -m src.run SW1A2AA
tests/
├── test_agents.py            # Agent unit tests
├── test_graph.py             # End-to-end graph test
```

## 2. Dependencies to Add

```
langchain-google-genai        # Already installed (Phase 1)
langchain-openai              # Already installed (Phase 1)
langgraph                     # Already installed (Phase 1)
```

No new dependencies needed.

## 3. LangGraph State Schema (`src/agents/state.py`)

This is the shared state that flows through all nodes. Use `Annotated` with `operator.add` reducer for keys written by parallel nodes.

```python
import operator
from typing import Annotated
from typing_extensions import TypedDict

class ComplianceState(TypedDict):
    # Input
    postcode: str
    company_name: str  # Optional — property management company to verify

    # Agent 1 output: legal requirements checklist
    legal_requirements: Annotated[list[dict], operator.add]
    # Each dict: {"requirement": str, "legislation": str, "section": str, "source_url": str}

    # Agent 2 output: property data from real APIs
    epc_data: dict
    # {"rating": str, "expiry_date": str, "address": str, "lodgement_date": str, "found": bool}
    company_data: dict
    # {"company_name": str, "status": str, "company_number": str, "found": bool}

    # Agent 3 output: risk assessment
    risk_score: int           # 0-100
    risk_level: str           # "GREEN" | "AMBER" | "RED"
    violations: list[dict]    # [{"description": str, "severity": str, "legislation": str}]
    warnings: list[dict]      # [{"description": str, "expires_in_days": int | None}]

    # Orchestrator output
    summary: str              # Human-readable verdict
    raw_agent_outputs: Annotated[list[dict], operator.add]
    # Collects each agent's output for debugging/audit trail
```

**Critical:** `legal_requirements` and `raw_agent_outputs` use the `operator.add` reducer because Agents 1 and 2 run in parallel and both append to `raw_agent_outputs`. Without the reducer, LangGraph will raise `INVALID_CONCURRENT_GRAPH_UPDATE`.

## 4. Agent 1: Legal Rules Agent (`src/agents/legal_rules.py`)

**Model:** Gemini 2.5 Flash via `langchain-google-genai`
**Role:** Query the RAG vector store for applicable compliance requirements, return a structured checklist with citations.

```python
from langchain.chat_models import init_chat_model
from src.rag.store import query_legislation
from src.agents.state import ComplianceState

# Initialize Gemini Flash
llm = init_chat_model("google_genai:gemini-2.5-flash")

SYSTEM_PROMPT = """You are a UK housing compliance expert. Given relevant legislation excerpts,
extract the specific compliance requirements that apply to letting a residential property.

For each requirement, provide:
- requirement: A clear, one-sentence description of what must be satisfied
- legislation: The name of the act/regulation (e.g., "Energy Efficiency Regulations 2015")
- section: The specific section or regulation number
- source_url: The URL to the legislation source

Return your answer as a JSON array of requirement objects. Only include requirements that are
directly relevant to letting a residential property in England/Wales. Be specific and cite
exact sections. Do not invent requirements — only use what is in the provided legislation excerpts."""

async def legal_rules_agent(state: ComplianceState) -> dict:
    """Query RAG for applicable legal requirements and structure them."""
    postcode = state["postcode"]

    # Query the vector store for relevant legislation
    rag_results = query_legislation(
        f"compliance requirements for letting a residential property, EPC, safety certificates, tenancy regulations",
        k=10,
    )

    # Format the RAG context for the LLM
    context_chunks = []
    for r in rag_results:
        meta = r["metadata"]
        context_chunks.append(
            f"[{meta.get('act_name', 'Unknown')} — {meta.get('section_title', 'Unknown')}]\n{r['content']}"
        )
    context = "\n\n---\n\n".join(context_chunks)

    # Ask Gemini to extract structured requirements
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Property postcode: {postcode}\n\nRelevant legislation excerpts:\n\n{context}"},
    ]

    response = await llm.ainvoke(messages)

    # Parse the JSON response
    import json
    try:
        # Strip markdown code fences if present
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        requirements = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        requirements = [{"requirement": "Unable to parse legal requirements", "legislation": "N/A", "section": "N/A", "source_url": ""}]

    return {
        "legal_requirements": requirements,
        "raw_agent_outputs": [{"agent": "legal_rules", "output": requirements}],
    }
```

## 5. Agent 2: Property Audit Agent (`src/agents/property_audit.py`)

**Model:** GPT-4o-mini via `langchain-openai`
**Role:** Pull real property data from EPC and Companies House APIs, return structured findings.

```python
from langchain.chat_models import init_chat_model
from src.api.epc import EPCClient
from src.api.companies_house import CompaniesHouseClient
from src.config import get_config
from src.agents.state import ComplianceState

llm = init_chat_model("openai:gpt-4o-mini")

async def property_audit_agent(state: ComplianceState) -> dict:
    """Check real property data against compliance requirements."""
    config = get_config()
    postcode = state["postcode"]
    company_name = state.get("company_name", "")

    # --- EPC Check ---
    epc_client = EPCClient(config.epc_api_key)
    try:
        certs = await epc_client.search_by_postcode(postcode)
        latest = epc_client.get_latest_certificate(certs)
        if latest:
            epc_data = {
                "found": True,
                "rating": latest.current_energy_rating,
                "potential_rating": latest.potential_energy_rating,
                "lodgement_date": latest.lodgement_date,
                "address": latest.address,
                "property_type": latest.property_type,
            }
        else:
            epc_data = {"found": False, "rating": None, "error": "No EPC certificates found for this postcode"}
    except Exception as e:
        epc_data = {"found": False, "rating": None, "error": str(e)}

    # --- Companies House Check ---
    company_data = {"found": False, "status": None, "company_name": company_name}
    if company_name:
        ch_client = CompaniesHouseClient(config.companies_house_api_key)
        try:
            results = await ch_client.search_company(company_name)
            if results:
                top = results[0]
                company_data = {
                    "found": True,
                    "company_name": top.company_name,
                    "company_number": top.company_number,
                    "status": top.company_status,
                    "type": top.type,
                }
        except Exception as e:
            company_data = {"found": False, "status": None, "company_name": company_name, "error": str(e)}

    return {
        "epc_data": epc_data,
        "company_data": company_data,
        "raw_agent_outputs": [{"agent": "property_audit", "output": {"epc": epc_data, "company": company_data}}],
    }
```

**Note:** This agent does NOT use the LLM for the core logic — it calls real APIs and returns structured data directly. The LLM is available for edge cases (e.g., interpreting ambiguous API responses) but the primary path is deterministic.

## 6. Agent 3: Risk Scorer (`src/agents/risk_scorer.py`)

**Model:** GPT-4o-mini via `langchain-openai`
**Role:** Takes outputs from Agents 1 and 2, scores risk, classifies property.

```python
import json
from langchain.chat_models import init_chat_model
from src.agents.state import ComplianceState

llm = init_chat_model("openai:gpt-4o-mini")

SYSTEM_PROMPT = """You are a UK property compliance risk assessor. Given:
1. A list of legal requirements that must be satisfied
2. Real property data (EPC rating, company status)

Score the property's compliance risk from 0-100 and classify it:
- GREEN (0-29): Fully compliant, clear to lease
- AMBER (30-69): Minor issues or upcoming expirations, proceed with caution
- RED (70-100): Hard legal violations, DO NOT lease

Scoring rules:
- No EPC on record → RED (score 90). This is itself a compliance violation.
- EPC rating F or G → RED (score 95). Illegal to let since April 2020. Fine up to £30,000.
- EPC rating E with lodgement > 9 years ago → AMBER (score 50). Approaching expiry.
- EPC rating D or above, valid → GREEN contribution.
- Company status "dissolved" or "liquidation" → RED (score 85).
- Company not found → AMBER (score 40). May be sole trader.
- Company status "active" → GREEN contribution.

Return your assessment as JSON:
{
    "risk_score": <int 0-100>,
    "risk_level": "<GREEN|AMBER|RED>",
    "violations": [{"description": "<what's wrong>", "severity": "<CRITICAL|HIGH|MEDIUM>", "legislation": "<which law>"}],
    "warnings": [{"description": "<what to watch>", "expires_in_days": <int or null>}]
}"""

async def risk_scorer_agent(state: ComplianceState) -> dict:
    """Score the property's compliance risk based on legal requirements and property data."""
    epc_data = state.get("epc_data", {})
    company_data = state.get("company_data", {})
    legal_requirements = state.get("legal_requirements", [])

    user_message = f"""Property Data:
- EPC: {json.dumps(epc_data, indent=2)}
- Company: {json.dumps(company_data, indent=2)}

Legal Requirements:
{json.dumps(legal_requirements, indent=2)}

Assess this property's compliance risk."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = await llm.ainvoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        # Fallback: if parsing fails, default to AMBER
        result = {
            "risk_score": 50,
            "risk_level": "AMBER",
            "violations": [],
            "warnings": [{"description": "Risk assessment parsing failed — manual review needed", "expires_in_days": None}],
        }

    return {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "violations": result.get("violations", []),
        "warnings": result.get("warnings", []),
        "raw_agent_outputs": [{"agent": "risk_scorer", "output": result}],
    }
```

## 7. Orchestrator (`src/agents/orchestrator.py`)

**Model:** GPT-4o via `langchain-openai`
**Role:** Generates the final human-readable summary after all agents complete.

```python
import json
from langchain.chat_models import init_chat_model
from src.agents.state import ComplianceState

llm = init_chat_model("openai:gpt-4o")

SYSTEM_PROMPT = """You are the final compliance report writer. Given the risk assessment results,
write a clear, professional summary in 3-5 sentences. Include:
1. The overall verdict (GREEN/AMBER/RED) and what it means
2. The key findings (EPC status, company status)
3. Any critical violations that must be resolved before leasing
4. Any warnings to monitor

Be direct, professional, and specific. This summary will be read by property managers."""

async def orchestrator_summarize(state: ComplianceState) -> dict:
    """Generate the final human-readable compliance summary."""
    user_message = f"""Compliance Check Results for {state['postcode']}:

Risk Level: {state.get('risk_level', 'UNKNOWN')}
Risk Score: {state.get('risk_score', 'N/A')}/100

EPC Data: {json.dumps(state.get('epc_data', {}), indent=2)}
Company Data: {json.dumps(state.get('company_data', {}), indent=2)}

Violations: {json.dumps(state.get('violations', []), indent=2)}
Warnings: {json.dumps(state.get('warnings', []), indent=2)}

Legal Requirements Checked: {len(state.get('legal_requirements', []))}

Write the final compliance summary."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = await llm.ainvoke(messages)

    return {"summary": response.content}
```

## 8. LangGraph Graph Definition (`src/agents/graph.py`)

This is the core wiring. Fan-out Agents 1 & 2 in parallel, converge to Agent 3, then Orchestrator summarizes.

```python
from langgraph.graph import StateGraph, START, END
from src.agents.state import ComplianceState
from src.agents.legal_rules import legal_rules_agent
from src.agents.property_audit import property_audit_agent
from src.agents.risk_scorer import risk_scorer_agent
from src.agents.orchestrator import orchestrator_summarize


def build_compliance_graph():
    """Build and compile the compliance checking LangGraph."""
    builder = StateGraph(ComplianceState)

    # Add nodes
    builder.add_node("legal_rules", legal_rules_agent)
    builder.add_node("property_audit", property_audit_agent)
    builder.add_node("risk_scorer", risk_scorer_agent)
    builder.add_node("summarize", orchestrator_summarize)

    # Fan-out: START → legal_rules AND property_audit (parallel)
    builder.add_edge(START, "legal_rules")
    builder.add_edge(START, "property_audit")

    # Fan-in: both converge to risk_scorer
    # Use defer=True so risk_scorer waits for BOTH parallel branches
    builder.add_node("risk_scorer", risk_scorer_agent, defer=True)
    builder.add_edge("legal_rules", "risk_scorer")
    builder.add_edge("property_audit", "risk_scorer")

    # Sequential: risk_scorer → summarize → END
    builder.add_edge("risk_scorer", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()


# Pre-compiled graph instance
compliance_graph = build_compliance_graph()
```

**IMPORTANT for Gemini:** The `defer=True` on risk_scorer ensures it waits for both parallel branches to complete before executing. Without this, if one branch finishes before the other, risk_scorer might run with incomplete data. Check the LangGraph docs — if `defer` is not supported in the installed version, use `add_node` without defer and the fan-in edges will handle it (LangGraph waits for all incoming edges by default when a node has multiple predecessors).

## 9. CLI Entry Point (`src/run.py`)

```python
"""CLI entry point: python -m src.run <postcode> [--company <name>]"""
import asyncio
import argparse
import json
from dotenv import load_dotenv

load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="Aloft Compliance Firewall")
    parser.add_argument("postcode", help="UK postcode to check")
    parser.add_argument("--company", default="", help="Property management company name to verify")
    args = parser.parse_args()

    from src.agents.graph import compliance_graph

    print(f"\n{'='*60}")
    print(f"  COMPLIANCE CHECK: {args.postcode}")
    print(f"{'='*60}\n")

    result = await compliance_graph.ainvoke({
        "postcode": args.postcode,
        "company_name": args.company,
        "legal_requirements": [],
        "epc_data": {},
        "company_data": {},
        "risk_score": 0,
        "risk_level": "",
        "violations": [],
        "warnings": [],
        "summary": "",
        "raw_agent_outputs": [],
    })

    # Display results
    level = result["risk_level"]
    score = result["risk_score"]

    level_colors = {"GREEN": "✅", "AMBER": "⚠️", "RED": "🚫"}
    icon = level_colors.get(level, "❓")

    print(f"  {icon} VERDICT: {level} (Score: {score}/100)")
    print(f"\n{'─'*60}")
    print(f"\n{result['summary']}")

    if result["violations"]:
        print(f"\n{'─'*60}")
        print("  VIOLATIONS:")
        for v in result["violations"]:
            print(f"    🚫 [{v.get('severity', 'HIGH')}] {v['description']}")
            if v.get("legislation"):
                print(f"       Legislation: {v['legislation']}")

    if result["warnings"]:
        print(f"\n{'─'*60}")
        print("  WARNINGS:")
        for w in result["warnings"]:
            print(f"    ⚠️  {w['description']}")

    print(f"\n{'─'*60}")
    print(f"  EPC: {json.dumps(result['epc_data'], indent=4)}")
    print(f"\n{'─'*60}")
    print(f"  Legal requirements checked: {len(result['legal_requirements'])}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
```

## 10. Tests

### `tests/test_agents.py` — Unit tests for individual agents

```python
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
    mock_epc_certs = [MagicMock(
        current_energy_rating="D",
        potential_energy_rating="C",
        lodgement_date="2022-01-01",
        address="1 Test St",
        property_type="House",
    )]

    with patch("src.agents.property_audit.EPCClient") as mock_epc_cls, \
         patch("src.agents.property_audit.get_config") as mock_config:
        mock_config.return_value = MagicMock(epc_api_key="test", companies_house_api_key="test")
        mock_epc = AsyncMock()
        mock_epc.search_by_postcode.return_value = mock_epc_certs
        mock_epc.get_latest_certificate.return_value = mock_epc_certs[0]
        mock_epc_cls.return_value = mock_epc

        from src.agents.property_audit import property_audit_agent
        result = await property_audit_agent(make_base_state())

        assert result["epc_data"]["found"] is True
        assert result["epc_data"]["rating"] == "D"


@pytest.mark.asyncio
async def test_risk_scorer_red_for_low_epc():
    """Test that risk scorer returns RED for EPC rating F."""
    mock_response = MagicMock()
    mock_response.content = '{"risk_score": 95, "risk_level": "RED", "violations": [{"description": "EPC below minimum E", "severity": "CRITICAL", "legislation": "Energy Efficiency Regulations 2015"}], "warnings": []}'

    with patch("src.agents.risk_scorer.llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        from src.agents.risk_scorer import risk_scorer_agent
        state = make_base_state(
            epc_data={"found": True, "rating": "F", "lodgement_date": "2023-01-01"},
            legal_requirements=[{"requirement": "Minimum EPC E", "legislation": "Energy Efficiency Regulations 2015", "section": "Reg 23", "source_url": ""}],
        )
        result = await risk_scorer_agent(state)

        assert result["risk_level"] == "RED"
        assert result["risk_score"] >= 70
        assert len(result["violations"]) > 0
```

### `tests/test_graph.py` — End-to-end graph test (mocked APIs + LLMs)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_full_graph_execution():
    """Test the full graph runs end-to-end with mocked dependencies."""
    # Mock all LLMs
    legal_response = MagicMock()
    legal_response.content = '[{"requirement": "Minimum EPC E", "legislation": "Energy Efficiency Regulations 2015", "section": "Reg 23", "source_url": "https://legislation.gov.uk"}]'

    risk_response = MagicMock()
    risk_response.content = '{"risk_score": 15, "risk_level": "GREEN", "violations": [], "warnings": []}'

    summary_response = MagicMock()
    summary_response.content = "This property is fully compliant and clear to lease."

    # Mock EPC API
    mock_epc_cert = MagicMock(
        current_energy_rating="C", potential_energy_rating="B",
        lodgement_date="2023-06-01", address="1 Test St", property_type="House",
    )

    with patch("src.agents.legal_rules.llm") as mock_legal_llm, \
         patch("src.agents.legal_rules.query_legislation") as mock_rag, \
         patch("src.agents.risk_scorer.llm") as mock_risk_llm, \
         patch("src.agents.orchestrator.llm") as mock_orch_llm, \
         patch("src.agents.property_audit.EPCClient") as mock_epc_cls, \
         patch("src.agents.property_audit.get_config") as mock_config:

        mock_legal_llm.ainvoke = AsyncMock(return_value=legal_response)
        mock_rag.return_value = [{"content": "test", "metadata": {"act_name": "Test Act", "section_title": "S1"}, "relevance_score": 0.9}]
        mock_risk_llm.ainvoke = AsyncMock(return_value=risk_response)
        mock_orch_llm.ainvoke = AsyncMock(return_value=summary_response)
        mock_config.return_value = MagicMock(epc_api_key="test", companies_house_api_key="test")
        mock_epc = AsyncMock()
        mock_epc.search_by_postcode.return_value = [mock_epc_cert]
        mock_epc.get_latest_certificate.return_value = mock_epc_cert
        mock_epc_cls.return_value = mock_epc

        from src.agents.graph import build_compliance_graph
        graph = build_compliance_graph()

        result = await graph.ainvoke({
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
        })

        assert result["risk_level"] == "GREEN"
        assert result["risk_score"] == 15
        assert "compliant" in result["summary"].lower()
        assert len(result["raw_agent_outputs"]) >= 2  # At least legal + audit agents reported
```

## 11. Acceptance Criteria

Phase 2 is DONE when:

- [ ] `python -m src.run "SW1A 2AA"` runs end-to-end and returns a verdict
- [ ] Agents 1 & 2 execute in parallel (verify via timing — total should be < sum of individual times)
- [ ] Agent 1 returns real legal citations from the RAG store
- [ ] Agent 2 returns real EPC data from the live API
- [ ] Agent 3 correctly classifies: F-rated property → RED, C-rated → GREEN
- [ ] Orchestrator generates a readable summary
- [ ] All tests pass: `pytest tests/ -v`
- [ ] All code passes: `ruff check src/ tests/`

## 12. Notes for Gemini (Executor)

- **LLM initialization:** Use `init_chat_model("openai:gpt-4o-mini")` and `init_chat_model("google_genai:gemini-2.5-flash")`. This is the LangChain universal init — it handles provider detection from the prefix. Make sure `OPENAI_API_KEY` and `GOOGLE_API_KEY` are in `.env`.

- **`defer=True` on risk_scorer:** This is the LangGraph way to ensure a node waits for ALL incoming edges. If `defer` isn't supported in the installed version, remove it — LangGraph should still wait for all predecessor edges by default. Test and verify.

- **`add_node` called twice:** In the spec's `graph.py`, `risk_scorer` is added twice (once normally, once with defer). This is intentional to show the defer pattern — in practice, only call `add_node` once. Use whichever form works.

- **JSON parsing from LLMs:** Both Agents 1 and 3 expect JSON responses. The code strips markdown code fences (`\`\`\`json ... \`\`\``). If you want more reliability, use OpenAI's `response_format={"type": "json_object"}` for GPT-4o-mini, and for Gemini you can set `generation_config={"response_mime_type": "application/json"}`.

- **Property audit is mostly deterministic:** Agent 2 calls real APIs and returns structured data. The LLM is initialized but not used in the main path — it's there for future edge case handling. Don't add unnecessary LLM calls.

- **Test with real postcodes:** After getting it working with mocks, test with real postcodes. Good ones to try:
  - `SW1A 2AA` — Westminster, should have many EPC records
  - `E1 6AN` — East London, likely has older properties with lower ratings
  - `M1 1AA` — Manchester city centre

- **Don't duplicate the graph compilation.** The spec shows `compliance_graph = build_compliance_graph()` as a module-level singleton. This is fine for the demo. Don't create a new graph per request.

---

*Document version: 1.2*
*Created: 2026-03-09*
*Phase 1 spec added: 2026-03-09*
*Phase 2 spec added: 2026-03-09*
*Status: Phase 2 spec ready for Gemini execution*
