import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.epc import EPCClient
from src.models.schemas import EPCCertificate
from tests.conftest import MOCK_EPC_RESPONSE


@pytest.mark.asyncio
async def test_epc_search_by_postcode():
    # httpx responses are sync objects — use MagicMock, not AsyncMock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = MOCK_EPC_RESPONSE

    with patch("src.api.epc.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        client = EPCClient(api_key="test-key")
        certs = await client.search_by_postcode("SW1A 2AA")

        assert len(certs) == 1
        assert certs[0].current_energy_rating == "D"
        assert certs[0].postcode == "SW1A 2AA"

        # Verify postcode was cleaned (spaces removed)
        call_kwargs = mock_client.get.call_args
        assert call_kwargs.kwargs["params"]["postcode"] == "SW1A2AA"


def test_get_latest_certificate():
    client = EPCClient(api_key="test-key")
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


def test_get_latest_certificate_empty():
    client = EPCClient(api_key="test-key")
    assert client.get_latest_certificate([]) is None
