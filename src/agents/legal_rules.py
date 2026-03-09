from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.rag.store import query_legislation
from src.agents.state import ComplianceState

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


class LegalRequirement(BaseModel):
    requirement: str = Field(
        description="A clear, one-sentence description of what must be satisfied"
    )
    legislation: str = Field(
        description="The name of the act/regulation (e.g., 'Energy Efficiency Regulations 2015')"
    )
    section: str = Field(description="The specific section or regulation number")
    source_url: str = Field(description="The URL to the legislation source")


class LegalRequirementsOutput(BaseModel):
    requirements: list[LegalRequirement]


structured_llm = llm.with_structured_output(LegalRequirementsOutput)

SYSTEM_PROMPT = """You are a UK housing compliance expert. Given relevant legislation excerpts,
extract the specific compliance requirements that apply to letting a residential property.

Only include requirements that are directly relevant to letting a residential property in England/Wales.
Be specific and cite exact sections. Do not invent requirements — only use what is in the provided legislation excerpts."""


async def legal_rules_agent(state: ComplianceState) -> dict:
    """Query RAG for applicable legal requirements and structure them."""
    postcode = state["postcode"]

    # Query the vector store for relevant legislation
    rag_results = query_legislation(
        "compliance requirements for letting a residential property, EPC, safety certificates, tenancy regulations",
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
        {
            "role": "user",
            "content": f"Property postcode: {postcode}\n\nRelevant legislation excerpts:\n\n{context}",
        },
    ]

    try:
        response = await structured_llm.ainvoke(messages)
        requirements = [r.model_dump() for r in response.requirements]
    except Exception as e:
        requirements = [
            {
                "requirement": f"Error extracting legal requirements: {e}",
                "legislation": "N/A",
                "section": "N/A",
                "source_url": "",
            }
        ]

    return {
        "legal_requirements": requirements,
        "raw_agent_outputs": [{"agent": "legal_rules", "output": requirements}],
    }
