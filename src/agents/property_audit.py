from src.api.epc import EPCClient
from src.api.companies_house import CompaniesHouseClient
from src.config import get_config
from src.agents.state import ComplianceState


async def property_audit_agent(state: ComplianceState) -> dict:
    """Check real property data against compliance requirements."""
    config = get_config()
    postcode = state.get("postcode", "")
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
            epc_data = {
                "found": False,
                "rating": None,
                "error": "No EPC certificates found for this postcode",
            }
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
            company_data = {
                "found": False,
                "status": None,
                "company_name": company_name,
                "error": str(e),
            }

    return {
        "epc_data": epc_data,
        "company_data": company_data,
        "raw_agent_outputs": [
            {
                "agent": "property_audit",
                "output": {"epc": epc_data, "company": company_data},
            }
        ],
    }
