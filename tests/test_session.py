import json
from unittest.mock import AsyncMock, patch
from uuid import UUID

import aresponses
import pytest

from aioplatega.enums import PaymentMethodInt
from aioplatega.exceptions import (
    ClientDecodeError,
    PlategaAPIError,
    PlategaBadRequestError,
    PlategaForbiddenError,
    PlategaNetworkError,
    PlategaNotFoundError,
    PlategaServerError,
    PlategaUnauthorizedError,
)
from aioplatega.methods import CreateTransaction, GetRate, GetTransactionStatus
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.types import (
    CreateTransactionResponse,
    PaymentDetails,
    RateResponse,
    TransactionStatusResponse,
)

API_HOST = "app.platega.io"
MERCHANT_ID = "test-merchant"
SECRET = "test-secret"


@pytest.fixture
def session():
    return AiohttpSession()


class TestAiohttpSessionPost:
    async def test_create_transaction_success(self, session):
        tid = "12345678-1234-5678-1234-567812345678"
        response_body = {
            "transactionId": tid,
            "status": "PENDING",
        }

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=200,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )
            result = await session.make_request(MERCHANT_ID, SECRET, method)

            assert isinstance(result, CreateTransactionResponse)
            assert result.transaction_id == UUID(tid)
            assert result.status == "PENDING"

        await session.close()


class TestAiohttpSessionGet:
    async def test_get_transaction_status_success(self, session):
        tid = "12345678-1234-5678-1234-567812345678"
        response_body = {
            "id": tid,
            "status": "CONFIRMED",
        }

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                f"/transaction/{tid}",
                "GET",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=200,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = GetTransactionStatus(
                transaction_id=UUID(tid),
            )
            result = await session.make_request(MERCHANT_ID, SECRET, method)

            assert isinstance(result, TransactionStatusResponse)
            assert result.id == UUID(tid)
            assert result.status == "CONFIRMED"

        await session.close()

    async def test_get_rate_success(self, session):
        response_body = {
            "paymentMethod": 2,
            "currencyFrom": "RUB",
            "currencyTo": "USDT",
            "rate": 0.0105,
        }

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/rates/payment_method_rate",
                "GET",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=200,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = GetRate(
                merchant_id=MERCHANT_ID,
                payment_method=2,
                currency_from="RUB",
                currency_to="USDT",
            )
            result = await session.make_request(MERCHANT_ID, SECRET, method)

            assert isinstance(result, RateResponse)
            assert result.rate == 0.0105

        await session.close()


class TestAiohttpSessionErrors:
    async def test_400_bad_request(self, session):
        response_body = {"message": "Invalid payment method"}

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=400,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(PlategaBadRequestError) as exc_info:
                await session.make_request(MERCHANT_ID, SECRET, method)

            assert exc_info.value.status_code == 400
            assert exc_info.value.message == "Invalid payment method"

        await session.close()

    async def test_401_unauthorized(self, session):
        response_body = {"message": "Invalid credentials"}

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=401,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(PlategaUnauthorizedError) as exc_info:
                await session.make_request(MERCHANT_ID, SECRET, method)

            assert exc_info.value.status_code == 401

        await session.close()

    async def test_403_forbidden(self, session):
        response_body = {"message": "Forbidden"}

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=403,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(PlategaForbiddenError):
                await session.make_request(MERCHANT_ID, SECRET, method)

        await session.close()

    async def test_404_not_found(self, session):
        response_body = {"message": "Not found"}

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=404,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(PlategaNotFoundError):
                await session.make_request(MERCHANT_ID, SECRET, method)

        await session.close()

    async def test_500_server_error(self, session):
        response_body = {"message": "Internal server error"}

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=500,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(PlategaServerError) as exc_info:
                await session.make_request(MERCHANT_ID, SECRET, method)

            assert exc_info.value.status_code == 500

        await session.close()

    async def test_non_json_error_response(self, session):
        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body="Bad Gateway",
                    content_type="text/plain",
                    status=502,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(PlategaAPIError):
                await session.make_request(MERCHANT_ID, SECRET, method)

        await session.close()

    async def test_non_json_success_response(self, session):
        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body="not json",
                    content_type="text/plain",
                    status=200,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(ClientDecodeError):
                await session.make_request(MERCHANT_ID, SECRET, method)

        await session.close()

    async def test_network_error(self, session):
        session._api_url = "http://app.platega.io"
        session._get_session()

        method = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )

        with (
            patch.object(
                session._session,
                "post",
                new_callable=AsyncMock,
                side_effect=ConnectionError("refused"),
            ),
            pytest.raises(PlategaNetworkError, match="refused"),
        ):
            await session.make_request(MERCHANT_ID, SECRET, method)

        await session.close()

    async def test_invalid_json_for_model(self, session):
        response_body = {"unexpectedField": "value"}

        async with aresponses.ResponsesMockServer() as arsps:
            arsps.add(
                API_HOST,
                "/transaction/process",
                "POST",
                aresponses.Response(
                    body=json.dumps(response_body),
                    content_type="application/json",
                    status=200,
                ),
            )
            session._api_url = "http://app.platega.io"

            method = CreateTransaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )

            with pytest.raises(ClientDecodeError, match="Failed to parse response"):
                await session.make_request(MERCHANT_ID, SECRET, method)

        await session.close()


class TestAiohttpSessionLifecycle:
    async def test_close(self, session):
        # Trigger session creation
        session._get_session()
        assert session._session is not None

        await session.close()
        assert session._session is None

    async def test_close_idempotent(self, session):
        await session.close()
        await session.close()  # should not raise

    async def test_lazy_session_creation(self):
        session = AiohttpSession()
        assert session._session is None

    async def test_custom_api_url(self):
        session = AiohttpSession(api_url="https://custom.api.com")
        assert session._api_url == "https://custom.api.com"
        await session.close()
