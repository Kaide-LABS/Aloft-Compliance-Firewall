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

*Document version: 1.1*
*Created: 2026-03-09*
*Phase 1 spec added: 2026-03-09*
*Status: Phase 1 spec ready for Gemini execution*
