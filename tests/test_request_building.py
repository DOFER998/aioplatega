"""How a method object becomes an HTTP request: path, query, and body.

These cover the split between fields that belong in the URL path and fields
that belong in the query string or JSON body — a field must land in exactly
one of them.
"""

from __future__ import annotations

import json
from typing import Any, ClassVar
from uuid import UUID

import pytest
from aiohttp import web

from aioplatega.enums import PaymentMethodInt
from aioplatega.methods import CreateTransaction, GetConversions, GetRate, GetTransactionStatus
from aioplatega.methods.base import PlategaMethod
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.types import PaymentDetails, TransactionStatusResponse
from tests.factories import MERCHANT_ID, SECRET, SUBSCRIPTION_ID, TRANSACTION_ID

TID = TRANSACTION_ID
SID = SUBSCRIPTION_ID
MERCHANT = MERCHANT_ID


@pytest.fixture
def session():
    return AiohttpSession()


class RecordingServer:
    """A real HTTP server that records what actually arrived on the wire.

    Asserting against aiohttp call arguments would test our intent; this tests
    the bytes, including how yarl renders query values into the URL.
    """

    def __init__(self, body: dict[str, Any]) -> None:
        self._body = body
        self.requests: list[dict[str, Any]] = []
        self._runner: web.AppRunner | None = None
        self.url = ""

    async def __aenter__(self) -> RecordingServer:
        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", self._handle)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await site.start()
        port = self._runner.addresses[0][1]
        self.url = f"http://127.0.0.1:{port}"
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self._runner is not None:
            await self._runner.cleanup()

    async def _handle(self, request: web.Request) -> web.Response:
        raw = await request.text()
        self.requests.append(
            {
                "method": request.method,
                "path": request.path,
                "raw_path": request.raw_path,
                "query": dict(request.query),
                "headers": dict(request.headers),
                "body": json.loads(raw) if raw else None,
            }
        )
        return web.json_response(self._body)


@pytest.fixture
def recording():
    return RecordingServer


class TestPathSubstitution:
    def test_path_placeholder_is_filled(self, session):
        method = GetTransactionStatus(transaction_id=UUID(TID))
        url, _ = session._build_url(method)
        assert url == f"https://app.platega.io/transaction/{TID}"

    def test_path_field_is_reported_as_consumed(self, session):
        method = GetTransactionStatus(transaction_id=UUID(TID))
        _, consumed = session._build_url(method)
        assert consumed == frozenset({"transaction_id"})

    def test_method_without_placeholders_consumes_nothing(self, session):
        method = GetRate(
            merchant_id=MERCHANT_ID,
            payment_method=2,
            currency_from="RUB",
            currency_to="USDT",
        )
        url, consumed = session._build_url(method)
        assert url == "https://app.platega.io/rates/payment_method_rate"
        assert consumed == frozenset()

    def test_path_value_is_url_quoted(self, session):
        """A value carrying path separators must not be able to rewrite the path."""

        class SlugMethod(PlategaMethod[TransactionStatusResponse]):
            __api_method__: ClassVar[str] = "/thing/{slug}"
            __http_method__: ClassVar[str] = "GET"
            __returning__: ClassVar[type] = TransactionStatusResponse

            slug: str

        url, consumed = session._build_url(SlugMethod(slug="../../admin?x=1"))
        assert url == "https://app.platega.io/thing/..%2F..%2Fadmin%3Fx%3D1"
        assert consumed == frozenset({"slug"})


class TestPayloadSeparation:
    def test_path_field_is_absent_from_payload(self, session):
        method = GetTransactionStatus(transaction_id=UUID(TID))
        _, consumed = session._build_url(method)
        payload = session._build_payload(method, consumed)
        assert payload == {}

    def test_non_path_fields_survive_in_payload(self, session):
        method = GetRate(
            merchant_id=MERCHANT_ID,
            payment_method=2,
            currency_from="RUB",
            currency_to="USDT",
        )
        _, consumed = session._build_url(method)
        payload = session._build_payload(method, consumed)
        assert payload == {
            "merchantId": MERCHANT_ID,
            "paymentMethod": 2,
            "currencyFrom": "RUB",
            "currencyTo": "USDT",
        }

    def test_payload_is_json_primitive(self, session):
        """No UUID/datetime objects may reach aiohttp — they get mangled or rejected."""
        method = GetTransactionStatus(transaction_id=UUID(TID))
        payload = session._build_payload(method, frozenset())
        assert payload["transactionId"] == TID
        json.dumps(payload)

    def test_none_fields_are_dropped(self, session):
        method = GetConversions()
        payload = session._build_payload(method, frozenset())
        assert payload == {"page": 0, "size": 20}


class TestQuerySerialization:
    def test_query_values_are_strings(self, session):
        method = GetConversions(page=2, size=50)
        query = session._to_query({"page": 2, "size": 50, "flag": True, "none": None})
        assert query == {"page": "2", "size": "50", "flag": "true"}
        assert method.page == 2

    def test_uuid_is_not_rendered_as_integer(self, session):
        """yarl coerces UUID via __int__, producing a 128-bit number in the URL."""
        method = GetTransactionStatus(transaction_id=UUID(TID))
        query = session._to_query(session._build_payload(method, frozenset()))
        assert query["transactionId"] == TID


class TestRequestOnTheWire:
    """End-to-end against a real socket, so yarl's URL rendering is included."""

    async def test_get_transaction_status_sends_no_query_string(self, session, recording):
        async with recording({"id": TID, "status": "CONFIRMED"}) as server:
            session._api_url = server.url
            await session.make_request(
                MERCHANT_ID, SECRET, GetTransactionStatus(transaction_id=UUID(TID))
            )
            await session.close()

        (req,) = server.requests
        assert req["method"] == "GET"
        assert req["path"] == f"/transaction/{TID}"
        assert req["query"] == {}
        assert req["raw_path"] == f"/transaction/{TID}"

    async def test_credentials_travel_in_headers(self, session, recording):
        async with recording({"id": TID, "status": "CONFIRMED"}) as server:
            session._api_url = server.url
            await session.make_request(
                MERCHANT_ID, SECRET, GetTransactionStatus(transaction_id=UUID(TID))
            )
            await session.close()

        (req,) = server.requests
        assert req["headers"]["X-MerchantId"] == MERCHANT_ID
        assert req["headers"]["X-Secret"] == SECRET

    async def test_get_rate_sends_all_fields_as_query(self, session, recording):
        async with recording({"rate": 0.0105}) as server:
            session._api_url = server.url
            await session.make_request(
                MERCHANT_ID,
                SECRET,
                GetRate(
                    merchant_id=MERCHANT_ID,
                    payment_method=PaymentMethodInt.SBP_QR,
                    currency_from="RUB",
                    currency_to="USDT",
                ),
            )
            await session.close()

        (req,) = server.requests
        assert req["query"] == {
            "merchantId": MERCHANT_ID,
            "paymentMethod": "2",
            "currencyFrom": "RUB",
            "currencyTo": "USDT",
        }

    async def test_post_sends_json_body_and_no_query(self, session, recording):
        async with recording({"transactionId": TID, "status": "PENDING"}) as server:
            session._api_url = server.url
            await session.make_request(
                MERCHANT_ID,
                SECRET,
                CreateTransaction(
                    payment_method=PaymentMethodInt.SBP_QR,
                    payment_details=PaymentDetails(amount=100.0, currency="RUB"),
                ),
            )
            await session.close()

        (req,) = server.requests
        assert req["method"] == "POST"
        assert req["query"] == {}
        assert req["body"] == {
            "paymentMethod": 2,
            "paymentDetails": {"amount": 100.0, "currency": "RUB"},
        }


class TestStandardHeaders:
    """The vendor SDK sends Accept and User-Agent; several endpoints list
    ``accept`` as a required header, and a User-Agent lets Platega attribute
    traffic when a merchant asks them to debug an integration."""

    async def test_accept_and_user_agent_are_sent(self, session, recording):
        async with recording({"id": TID, "status": "CONFIRMED"}) as server:
            session._api_url = server.url
            await session.make_request(
                MERCHANT_ID, SECRET, GetTransactionStatus(transaction_id=UUID(TID))
            )
            await session.close()

        (req,) = server.requests
        assert req["headers"]["Accept"] == "application/json"
        assert req["headers"]["User-Agent"].startswith("aioplatega/")

    async def test_headers_are_sent_on_post_too(self, session, recording):
        async with recording({"transactionId": TID, "status": "PENDING"}) as server:
            session._api_url = server.url
            await session.make_request(
                MERCHANT_ID,
                SECRET,
                CreateTransaction(
                    payment_method=PaymentMethodInt.SBP_QR,
                    payment_details=PaymentDetails(amount=100.0, currency="RUB"),
                ),
            )
            await session.close()

        (req,) = server.requests
        assert req["headers"]["Accept"] == "application/json"
        assert req["headers"]["User-Agent"].startswith("aioplatega/")
