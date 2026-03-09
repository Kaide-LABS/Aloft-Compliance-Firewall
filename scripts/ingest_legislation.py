import asyncio
from dotenv import load_dotenv
import os
import sys

# Add project root to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.ingest import ingest_all_legislation

load_dotenv()

if __name__ == "__main__":
    asyncio.run(ingest_all_legislation())
