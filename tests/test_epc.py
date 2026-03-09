import pytest
from src.api.epc import EPCClient
from src.models.schemas import EPCCertificate


@pytest.mark.asyncio
async def test_epc_client_mock():
    client = EPCClient(api_key="mock")
    certs = await client.search_by_postcode("SW1A 2AA")

    assert len(certs) == 1
    assert certs[0].current_energy_rating == "D"
    assert certs[0].postcode == "SW1A 2AA"


def test_get_latest_certificate():
    client = EPCClient(api_key="mock")
    certs = [
        EPCCertificate(
            **{
                "address": "1 Mock St",
                "postcode": "SW1A 2AA",
                "current-energy-rating": "D",
                "potential-energy-rating": "C",
                "property-type": "House",
                "lodgement-date": "2020-01-01",
                "certificate-hash": "1",
            }
        ),
        EPCCertificate(
            **{
                "address": "1 Mock St",
                "postcode": "SW1A 2AA",
                "current-energy-rating": "C",
                "potential-energy-rating": "B",
                "property-type": "House",
                "lodgement-date": "2022-01-01",
                "certificate-hash": "2",
            }
        ),
    ]

    latest = client.get_latest_certificate(certs)
    assert latest is not None
    assert latest.certificate_hash == "2"
