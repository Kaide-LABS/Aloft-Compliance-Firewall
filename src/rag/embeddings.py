from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os


def get_embedding_model():
    if os.environ.get("GOOGLE_API_KEY") == "mock":
        # Return a fake embedding model for mock testing
        from langchain_core.embeddings import FakeEmbeddings

        return FakeEmbeddings(size=768)

    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
    )
