"""Every failure a caller can hit must arrive as a PlategaError subclass.

Two directions are covered: errors the API returns (HTTP status mapping) and
errors raised before a request is ever sent (bad input). Genuine programming
errors must NOT be swallowed into the hierarchy — they should surface as-is.
"""

import json

import aresponses
import pytest

from aioplatega import Platega
from aioplatega.enums import PaymentMethodInt
from aioplatega.exceptions import (
    PlategaAPIError,
    PlategaConflictError,
    PlategaError,
    PlategaNetworkError,
    PlategaRateLimitError,
    PlategaUnprocessableEntityError,
    PlategaValidationError,
)
from aioplatega.methods import CreateTransaction
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.types import PaymentDetails
from tests.factories import MERCHANT_ID, SECRET, SUBSCRIPTION_ID, TRANSACTION_ID

TID = TRANSACTION_ID
SID = SUBSCRIPTION_ID
MERCHANT = MERCHANT_ID

API_HOST = "app.platega.io"


@pytest.fixture
def session():
    return AiohttpSession()


def _method() -> CreateTransaction:
    return CreateTransaction(
        payment_method=PaymentMethodInt.SBP_QR,
        payment_details=PaymentDetails(amount=100.0, currency="RUB"),
    )


class TestStatusMapping:
    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (409, PlategaConflictError),
            (422, PlategaUnprocessableEntityError),
            (429, PlategaRateLimitError),
        ],
    )
    async def test_status_maps_to_dedicated_type(self, session, status, expected):
        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps({"message": "nope"}),
                    content_type="application/json",
                    status=status,
                ),
            )
            session._api_url = "http://app.platega.io"

            with pytest.raises(expected) as exc_info:
                await session.make_request(MERCHANT_ID, SECRET, _method())

            assert exc_info.value.status_code == status
            assert isinstance(exc_info.value, PlategaAPIError)

        await session.close()


class TestInputValidation:
    async def test_bad_uuid_raises_platega_validation_error(self):
        client = Platega(merchant_id="m", secret="s")
        with pytest.raises(PlategaValidationError):
            await client.get_transaction_status("not-a-uuid")
        await client.close()

    async def test_validation_error_is_a_platega_error(self):
        client = Platega(merchant_id="m", secret="s")
        with pytest.raises(PlategaError):
            await client.get_transaction_status("not-a-uuid")
        await client.close()

    async def test_valid_uuid_string_is_accepted(self, mock_session):
        client = Platega(merchant_id="m", secret="s", session=mock_session)
        await client.get_transaction_status("12345678-1234-5678-1234-567812345678")
        assert len(mock_session.calls) == 1


class TestProgrammingErrorsAreNotMasked:
    async def test_unexpected_exception_is_not_reported_as_network_error(
        self, session, monkeypatch
    ):
        """A TypeError from our own code must not masquerade as connectivity loss."""
        session._api_url = "http://app.platega.io"
        client_session = session._get_session()

        def boom(*args, **kwargs):
            raise TypeError("bug in request construction")

        monkeypatch.setattr(client_session, "post", boom)

        with pytest.raises(TypeError, match="bug in request construction"):
            await session.make_request(MERCHANT_ID, SECRET, _method())

        await session.close()

    async def test_connection_failure_is_still_a_network_error(self, session, monkeypatch):
        session._api_url = "http://app.platega.io"
        client_session = session._get_session()

        def refuse(*args, **kwargs):
            raise ConnectionRefusedError("refused")

        monkeypatch.setattr(client_session, "post", refuse)

        with pytest.raises(PlategaNetworkError, match="refused"):
            await session.make_request(MERCHANT_ID, SECRET, _method())

        await session.close()
