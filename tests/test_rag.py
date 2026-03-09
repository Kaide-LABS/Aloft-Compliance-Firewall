import pytest
from unittest.mock import AsyncMock
from langchain_core.embeddings import FakeEmbeddings
from src.api.legislation import LegislationFetcher
from src.rag.store import get_vector_store
from src.rag.ingest import ingest_all_legislation
from tests.conftest import MOCK_LEGISLATION_XML


def test_extract_sections_from_xml():
    """Test that the XML parser extracts individual sections with metadata."""
    fetcher = LegislationFetcher()
    sections = fetcher.extract_sections_from_xml(MOCK_LEGISLATION_XML)

    assert len(sections) == 2
    assert sections[0]["section_number"] == "section-1"
    assert "Minimum energy efficiency" in sections[0]["title"]
    assert "EPC rating" in sections[0]["text"]
    assert sections[1]["section_number"] == "section-2"
    assert "30000" in sections[1]["text"]


def test_extract_sections_invalid_xml():
    """Test graceful handling of invalid XML."""
    fetcher = LegislationFetcher()
    sections = fetcher.extract_sections_from_xml("<broken>xml")

    assert len(sections) == 1
    assert sections[0]["section_number"] == "error"


@pytest.mark.asyncio
async def test_rag_ingest_and_query(monkeypatch):
    """Test full ingest + query pipeline with mocked APIs and embeddings."""
    # Mock the embedding model to avoid needing a real API key
    monkeypatch.setattr(
        "src.rag.store.get_embedding_model",
        lambda: FakeEmbeddings(size=768),
    )
    monkeypatch.setattr(
        "src.rag.ingest.get_vector_store",
        lambda create_if_missing=False: get_vector_store(create_if_missing),
    )

    # Mock the legislation fetcher to return our test XML
    mock_fetch = AsyncMock(return_value=MOCK_LEGISLATION_XML)
    monkeypatch.setattr(
        "src.rag.ingest.LegislationFetcher.fetch_legislation_xml",
        mock_fetch,
    )

    await ingest_all_legislation()

    # Query using the same fake embeddings
    from src.rag.store import query_legislation
    results = query_legislation("minimum EPC rating", k=1)

    assert len(results) >= 1
    assert "act_name" in results[0]["metadata"]
