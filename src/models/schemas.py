from pydantic import BaseModel, Field, ConfigDict


class EPCCertificate(BaseModel):
    address: str = Field(..., alias="address")
    postcode: str = Field(..., alias="postcode")
    current_energy_rating: str = Field(..., alias="current-energy-rating")
    potential_energy_rating: str = Field(..., alias="potential-energy-rating")
    property_type: str = Field(..., alias="property-type")
    lodgement_date: str = Field(..., alias="lodgement-date")
    certificate_hash: str = Field(..., alias="certificate-hash")

    model_config = ConfigDict(populate_by_name=True)


class EPCSearchResult(BaseModel):
    certificates: list[EPCCertificate]
    total_count: int


class CompanyProfile(BaseModel):
    company_name: str
    company_number: str
    company_status: str  # "active", "dissolved", etc.
    date_of_creation: str
    registered_office_address: dict
    type: str  # "ltd", "plc", etc.

    model_config = ConfigDict(populate_by_name=True)


class CompanySearchResult(BaseModel):
    items: list[CompanyProfile]
    total_results: int
