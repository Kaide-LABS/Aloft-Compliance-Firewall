from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.api.legislation import LegislationFetcher
from src.rag.store import get_vector_store, save_vector_store_docs

LEGISLATION_MANIFEST = [
    {
        "type": "ukpga",
        "year": 2004,
        "number": 34,
        "name": "Housing Act 2004",
        "sections": ["part/1", "part/2"],
    },
    {
        "type": "uksi",
        "year": 2015,
        "number": 962,
        "name": "Energy Efficiency Regulations 2015",
        "sections": [None],
    },
    {
        "type": "ukpga",
        "year": 1988,
        "number": 50,
        "name": "Housing Act 1988",
        "sections": ["schedule/2"],
    },
    {
        "type": "ukpga",
        "year": 2018,
        "number": 34,
        "name": "Homes (Fitness for Human Habitation) Act 2018",
        "sections": [None],
    },
]


async def ingest_all_legislation():
    fetcher = LegislationFetcher()
    store = get_vector_store(create_if_missing=True)
    all_documents = []

    for leg in LEGISLATION_MANIFEST:
        for section in leg["sections"]:
            print(f"Fetching {leg['name']} ({section or 'full'})...")
            try:
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
            except Exception as e:
                print(f"Failed to fetch {leg['name']} ({section}): {e}")

    # Chunk documents that are too long
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(all_documents)

    if chunks:
        # Add to Vector Store and persist the documents to disk
        store.add_documents(chunks)
        save_vector_store_docs(chunks)
        print(
            f"Ingested {len(chunks)} chunks from {len(LEGISLATION_MANIFEST)} pieces of legislation"
        )
    else:
        print("No documents to ingest.")
