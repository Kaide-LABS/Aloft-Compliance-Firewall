import pytest
import os
from src.rag.store import query_legislation
from src.rag.ingest import ingest_all_legislation


@pytest.mark.asyncio
async def test_rag_ingest_and_query():
    # Make sure we're using mock endpoints
    os.environ["GOOGLE_API_KEY"] = "mock"

    # Ingest mock data
    await ingest_all_legislation()

    # Query it
    results = query_legislation("minimum rating", k=1)

    assert len(results) == 1
    assert "mock legal section" in results[0]["content"]
    assert "act_name" in results[0]["metadata"]
