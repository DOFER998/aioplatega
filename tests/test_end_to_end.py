"""Every client method, end to end against a real socket.

The unit tests check method binding and the session checks serialization;
this closes the loop by driving the public client and asserting on what
actually left the process — path, verb, query and body together.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from aiohttp import web

from aioplatega import Platega
from aioplatega.enums import PaymentMethodInt, SubscriptionInterval
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.types import PaymentDetails, PaymentMetadata, SubscriptionPaymentDetails


def client_for(url: str) -> tuple[Platega, AiohttpSession]:
    """A client bound to the recording server, plus the session to close."""
    session = AiohttpSession(api_url=url)
    return Platega(merchant_id="m", secret="s", session=session), session


TID = "12345678-1234-5678-1234-567812345678"
SID = "11111111-1111-1111-1111-111111111111"


class Echo:
    """Answers every route with a canned body and records the request."""

    def __init__(self, payload: Any) -> None:
        self._payload = payload
        self.requests: list[dict[str, Any]] = []
        self._runner: web.AppRunner | None = None
        self.url = ""

    async def __aenter__(self) -> Echo:
        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", self._handle)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await site.start()
        self.url = f"http://127.0.0.1:{self._runner.addresses[0][1]}"
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._runner is not None:
            await self._runner.cleanup()

    async def _handle(self, request: web.Request) -> web.Response:
        body = await request.text()
        self.requests.append(
            {
                "method": request.method,
                "path": request.path,
                "query": dict(request.query),
                "body": json.loads(body) if body else None,
            }
        )
        return web.json_response(self._payload)


DETAILS = PaymentDetails(amount=100.0, currency="RUB")
SUB_DETAILS = SubscriptionPaymentDetails(
    amount=500, currency="RUB", interval=SubscriptionInterval.MONTH
)

CASES = [
    (
        "create_transaction",
        lambda c: c.create_transaction(
            payment_method=PaymentMethodInt.SBP_QR, payment_details=DETAILS
        ),
        "POST",
        "/transaction/process",
        {"transactionId": TID, "status": "PENDING"},
    ),
    (
        "create_payment_link",
        lambda c: c.create_payment_link(payment_details=DETAILS),
        "POST",
        "/v2/transaction/process",
        {"transactionId": TID, "status": "PENDING", "url": "https://pay"},
    ),
    (
        "get_transaction_status",
        lambda c: c.get_transaction_status(TID),
        "GET",
        f"/transaction/{TID}",
        {"id": TID, "status": "CONFIRMED"},
    ),
    ("get_h2h_qr", lambda c: c.get_h2h_qr(TID), "GET", f"/h2h/{TID}", {"amount": 1.0, "qr": "x"}),
    ("get_balances", lambda c: c.get_balances(), "GET", "/balance/all", [{"currency": "RUB"}]),
    (
        "get_conversions",
        lambda c: c.get_conversions(),
        "GET",
        "/transaction/balance-unlock-operations",
        {"content": [], "totalElements": 0},
    ),
    (
        "check_cancel_supported",
        lambda c: c.check_cancel_supported(TID),
        "GET",
        f"/transaction/{TID}/cancel-supported",
        {"supported": True},
    ),
    (
        "cancel_transaction",
        lambda c: c.cancel_transaction(TID),
        "POST",
        f"/transaction/{TID}/cancel",
        {"transactionId": TID, "accepted": True},
    ),
    (
        "export_transactions_csv",
        lambda c: c.export_transactions_csv(),
        "POST",
        "/transaction/export/csv",
        {"url": "https://f/x.csv"},
    ),
    (
        "export_transactions_excel",
        lambda c: c.export_transactions_excel(),
        "POST",
        "/transaction/export/excel",
        {"url": "https://f/x.xlsx"},
    ),
    (
        "export_transactions_json",
        lambda c: c.export_transactions_json(),
        "POST",
        "/transaction/export/json",
        [{"recordId": TID}],
    ),
    (
        "create_subscription",
        lambda c: c.create_subscription(payment_details=SUB_DETAILS, description="P"),
        "POST",
        "/transaction/process",
        {"transactionId": SID, "status": "PENDING"},
    ),
    (
        "get_subscription",
        lambda c: c.get_subscription(SID),
        "GET",
        f"/subscription/{SID}",
        {"id": SID},
    ),
    (
        "list_subscriptions",
        lambda c: c.list_subscriptions(),
        "GET",
        "/subscription",
        {"items": [], "total": 0, "page": 0, "size": 0},
    ),
    (
        "cancel_subscription",
        lambda c: c.cancel_subscription(SID),
        "POST",
        f"/subscription/{SID}/cancel",
        {"subscriptionId": SID, "status": "cancelled"},
    ),
    (
        "get_rate",
        lambda c: c.get_rate(payment_method=2, currency_from="RUB", currency_to="USDT"),
        "GET",
        "/rates/payment_method_rate",
        {"rate": 0.01},
    ),
]


@pytest.mark.parametrize(
    ("name", "call", "verb", "path", "response"), CASES, ids=[c[0] for c in CASES]
)
async def test_reaches_the_documented_endpoint(name, call, verb, path, response):
    async with Echo(response) as server:
        client, session = client_for(server.url)
        await call(client)
        await session.close()

    (req,) = server.requests
    assert req["method"] == verb
    assert req["path"] == path


class TestBodiesOnTheWire:
    async def test_subscription_body_carries_the_interval(self):
        async with Echo({"transactionId": SID, "status": "PENDING"}) as server:
            client, session = client_for(server.url)
            await client.create_subscription(payment_details=SUB_DETAILS, description="Premium")
            await session.close()

        assert server.requests[0]["body"] == {
            "paymentMethod": 6,
            "paymentDetails": {"amount": 500, "currency": "RUB", "interval": "3"},
            "description": "Premium",
        }

    async def test_metadata_reaches_the_wire(self):
        async with Echo({"transactionId": TID, "status": "PENDING"}) as server:
            client, session = client_for(server.url)
            await client.create_transaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=DETAILS,
                metadata=PaymentMetadata(user_id="u-1", user_name="Ivan"),
            )
            await session.close()

        assert server.requests[0]["body"]["metadata"] == {"userId": "u-1", "userName": "Ivan"}

    async def test_path_ids_never_leak_into_the_query(self):
        async with Echo({"id": TID, "status": "CONFIRMED"}) as server:
            client, session = client_for(server.url)
            await client.get_transaction_status(TID)
            await session.close()

        assert server.requests[0]["query"] == {}


class TestDocstringsMatchSignatures:
    """A documented argument that does not exist is worse than an undocumented one."""

    def test_every_documented_argument_exists(self):
        import inspect
        import re

        mismatches = []
        for name in dir(Platega):
            if name.startswith("_"):
                continue
            fn = getattr(Platega, name)
            if not callable(fn):
                continue
            doc = inspect.getdoc(fn) or ""
            block = re.search(r"Args:\n(.*?)(\n\n|\Z)", doc, re.S)
            if not block:
                continue
            documented = set(re.findall(r"^\s{4}(\w+):", block.group(1), re.M))
            actual = set(inspect.signature(fn).parameters) - {"self"}
            if documented - actual or actual - documented:
                mismatches.append((name, sorted(documented - actual), sorted(actual - documented)))

        assert mismatches == []
