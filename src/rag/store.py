import json
import os
from langchain_core.vectorstores import InMemoryVectorStore
from src.rag.embeddings import get_embedding_model
from langchain_core.documents import Document

PERSIST_FILE = "./data/in_memory/store.json"


def get_vector_store(create_if_missing: bool = False) -> InMemoryVectorStore:
    embedding = get_embedding_model()
    store = InMemoryVectorStore(embedding)

    if os.path.exists(PERSIST_FILE):
        with open(PERSIST_FILE, "r") as f:
            data = json.load(f)
            docs = [
                Document(page_content=d["content"], metadata=d["metadata"])
                for d in data
            ]
            store.add_documents(docs)
    elif not create_if_missing:
        print("Warning: Vector store file not found. Run ingest first.")

    return store


def save_vector_store(store: InMemoryVectorStore):
    os.makedirs(os.path.dirname(PERSIST_FILE), exist_ok=True)
    data = [
        {"content": d["text"], "metadata": d["metadata"]} for d in store.store.values()
    ]
    with open(PERSIST_FILE, "w") as f:
        json.dump(data, f)


def query_legislation(question: str, k: int = 5) -> list[dict]:
    """Query the vector store and return relevant legislation chunks with metadata."""
    store = get_vector_store()
    results = store.similarity_search_with_score(question, k=k)
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,  # act_name, section_number, title, etc.
            "relevance_score": score,
        }
        for doc, score in results
    ]
