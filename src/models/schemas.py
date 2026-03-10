from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EPCCertificate(BaseModel):
    address: str = Field(default="", alias="address")
    postcode: str = Field(default="", alias="postcode")
    current_energy_rating: str = Field(default="", alias="current-energy-rating")
    potential_energy_rating: str = Field(default="", alias="potential-energy-rating")
    property_type: str = Field(default="", alias="property-type")
    lodgement_date: str = Field(default="", alias="lodgement-date")
    certificate_hash: Optional[str] = Field(default=None, alias="certificate-hash")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class EPCSearchResult(BaseModel):
    certificates: list[EPCCertificate]
    total_count: int


class CompanyProfile(BaseModel):
    company_name: str = Field(default="", alias="title")
    company_number: str = Field(default="")
    company_status: str = Field(default="")  # "active", "dissolved", etc.
    date_of_creation: str = Field(default="")
    registered_office_address: dict = Field(default_factory=dict, alias="address")
    type: str = Field(default="", alias="company_type")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class CompanySearchResult(BaseModel):
    items: list[CompanyProfile]
    total_results: int
