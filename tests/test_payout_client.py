"""PayoutClient against a recording server: headers, bytes, and guardrails."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

import pytest
from aiohttp import web

from aioplatega.exceptions import PlategaError, PlategaUnauthorizedError
from aioplatega.payout import MAX_PAYOUT_RUB, MIN_PAYOUT_RUB, PayoutClient

MERCHANT = "29ef0000-0000-0000-0000-000000000000"
SECRET = "test-secret"

CARDS = [
    {
        "cardId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "masked": "•••• •••• •••• 4242",
        "last4": "4242",
        "brand": "Visa",
        "label": "Основная карта",
        "status": "ACTIVE",
    }
]
PAYOUT = {
    "withdrawalRecordId": "3c0d321d-40c4-46e3-97f0-7a8f50ce03a6",
    "status": "CREATED",
    "cardMasked": "**** 0000",
    "amountUsdtDebited": 13.270341,
}


class Recorder:
    def __init__(self, payload: Any, status: int = 200) -> None:
        self._payload = payload
        self._status = status
        self.requests: list[dict[str, Any]] = []
        self._runner: web.AppRunner | None = None
        self.url = ""

    async def __aenter__(self) -> Recorder:
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
        self.requests.append(
            {
                "method": request.method,
                "path": request.path,
                "query": dict(request.query),
                "headers": dict(request.headers),
                "raw_body": await request.read(),
            }
        )
        return web.json_response(self._payload, status=self._status)


def parse_auth(header: str) -> dict[str, str]:
    assert header.startswith("PG-HMAC ")
    return dict(part.strip().split("=", 1) for part in header.removeprefix("PG-HMAC ").split(","))


class TestGetCards:
    async def test_returns_iterable_cards(self):
        async with (
            Recorder(CARDS) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            cards = await client.get_cards()

        assert len(cards) == 1
        assert cards[0].last4 == "4242"
        assert [c.brand for c in cards] == ["Visa"]

    async def test_signs_with_the_empty_body_hash(self):
        async with (
            Recorder(CARDS) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.get_cards()

        (req,) = server.requests
        auth = parse_auth(req["headers"]["Authorization"])
        assert auth["kid"] == MERCHANT
        expected = base64.b64encode(
            hmac.new(
                SECRET.encode(),
                "\n".join(
                    ["GET", "/api/v1/cards", auth["ts"], "", hashlib.sha256(b"").hexdigest()]
                ).encode(),
                hashlib.sha256,
            ).digest()
        ).decode()
        assert auth["sig"] == expected

    async def test_get_carries_no_idempotency_key(self):
        async with (
            Recorder(CARDS) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.get_cards()

        assert "Idempotency-Key" not in server.requests[0]["headers"]

    async def test_only_active_flag(self):
        async with (
            Recorder(CARDS) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.get_cards(only_active=False)

        assert server.requests[0]["query"] == {"onlyActive": "false"}


class TestCreateCardPayout:
    async def test_signed_bytes_are_the_bytes_sent(self):
        """The signature covers the body; re-encoding it would invalidate the request."""
        async with (
            Recorder(PAYOUT) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.create_card_payout(
                card_number="2200000000000000",
                amount_rub=1500,
                idempotency_key="idem-1",
            )

        (req,) = server.requests
        auth = parse_auth(req["headers"]["Authorization"])
        body = req["raw_body"]
        assert b" " not in body
        expected = base64.b64encode(
            hmac.new(
                SECRET.encode(),
                "\n".join(
                    [
                        "POST",
                        "/api/v1/payouts/card-rub",
                        auth["ts"],
                        "idem-1",
                        hashlib.sha256(body).hexdigest(),
                    ]
                ).encode(),
                hashlib.sha256,
            ).digest()
        ).decode()
        assert auth["sig"] == expected

    async def test_body_shape(self):
        async with (
            Recorder(PAYOUT) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            result = await client.create_card_payout(card_id="card-1", amount_rub=2000)

        body = json.loads(server.requests[0]["raw_body"])
        assert body == {
            "cardId": "card-1",
            "amountRub": 2000,
            "payoutMethod": "CARD",
            "currencyRequested": "RUB",
        }
        assert result.status == "CREATED"
        assert result.amount_usdt_debited == 13.270341

    async def test_idempotency_key_is_echoed_in_the_header(self):
        async with (
            Recorder(PAYOUT) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.create_card_payout(
                card_id="c", amount_rub=1500, idempotency_key="idem-42"
            )

        assert server.requests[0]["headers"]["Idempotency-Key"] == "idem-42"

    async def test_a_key_is_generated_when_omitted(self):
        async with (
            Recorder(PAYOUT) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.create_card_payout(card_id="c", amount_rub=1500)

        assert server.requests[0]["headers"]["Idempotency-Key"]


class TestGuardrails:
    """Argument checks happen before the request: a sent payout cannot be recalled."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"card_id": "c", "card_number": "2200000000000000"},
            {},
        ],
    )
    async def test_exactly_one_card_reference_is_required(self, kwargs):
        client = PayoutClient(MERCHANT, SECRET)
        with pytest.raises(ValueError, match="exactly one"):
            await client.create_card_payout(amount_rub=1500, **kwargs)
        await client.close()

    @pytest.mark.parametrize("amount", [0, 999, MAX_PAYOUT_RUB + 1, -5])
    async def test_amount_must_be_within_the_documented_range(self, amount):
        client = PayoutClient(MERCHANT, SECRET)
        with pytest.raises(ValueError, match="amount_rub must be between"):
            await client.create_card_payout(card_id="c", amount_rub=amount)
        await client.close()

    @pytest.mark.parametrize("amount", [MIN_PAYOUT_RUB, MAX_PAYOUT_RUB])
    async def test_range_boundaries_are_accepted(self, amount):
        async with (
            Recorder(PAYOUT) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.create_card_payout(card_id="c", amount_rub=amount)
        assert len(server.requests) == 1


class TestErrors:
    async def test_http_error_maps_to_the_shared_hierarchy(self):
        async with (
            Recorder({"message": "bad signature"}, status=401) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            with pytest.raises(PlategaUnauthorizedError) as exc_info:
                await client.get_cards()

        assert exc_info.value.status_code == 401
        assert isinstance(exc_info.value, PlategaError)


class TestLifecycle:
    async def test_close_is_idempotent(self):
        client = PayoutClient(MERCHANT, SECRET)
        await client.close()
        await client.close()

    async def test_session_is_lazy(self):
        client = PayoutClient(MERCHANT, SECRET)
        assert client._session is None
        await client.close()


class TestPayoutTransportEdges:
    async def test_network_failure_becomes_a_network_error(self, monkeypatch):
        from aioplatega.exceptions import PlategaNetworkError

        client = PayoutClient(MERCHANT, SECRET)
        session = client._get_session()

        def refuse(*args: object, **kwargs: object) -> None:
            raise ConnectionRefusedError("refused")

        monkeypatch.setattr(session, "request", refuse)
        with pytest.raises(PlategaNetworkError, match="refused"):
            await client.get_cards()
        await client.close()

    async def test_non_json_error_body_still_raises_an_api_error(self):
        from aioplatega.exceptions import PlategaAPIError

        async def handler(request: web.Request) -> web.Response:
            return web.Response(body="Bad Gateway", content_type="text/plain", status=502)

        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        url = f"http://127.0.0.1:{runner.addresses[0][1]}"
        try:
            async with PayoutClient(MERCHANT, SECRET, api_url=url) as client:
                with pytest.raises(PlategaAPIError):
                    await client.get_cards()
        finally:
            await runner.cleanup()

    async def test_unparseable_success_body_is_a_decode_error(self):
        from aioplatega.exceptions import ClientDecodeError

        async def handler(request: web.Request) -> web.Response:
            return web.Response(body="not json", content_type="text/plain", status=200)

        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        url = f"http://127.0.0.1:{runner.addresses[0][1]}"
        try:
            async with PayoutClient(MERCHANT, SECRET, api_url=url) as client:
                with pytest.raises(ClientDecodeError):
                    await client.get_cards()
        finally:
            await runner.cleanup()

    async def test_unexpected_payload_shape_is_a_decode_error(self):
        from aioplatega.exceptions import ClientDecodeError

        async with (
            Recorder({"not": "a list"}) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            with pytest.raises(ClientDecodeError, match="Failed to parse response"):
                await client.get_cards()

    async def test_unexpected_payout_shape_is_a_decode_error(self):
        from aioplatega.exceptions import ClientDecodeError

        async with (
            Recorder([1, 2, 3]) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            with pytest.raises(ClientDecodeError, match="Failed to parse response"):
                await client.create_card_payout(card_id="c", amount_rub=1500)

    async def test_trailing_slash_in_base_url_does_not_double_up(self):
        async with (
            Recorder(CARDS) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url + "/") as client,
        ):
            await client.get_cards()
        assert server.requests[0]["path"] == "/api/v1/cards"


class TestPayoutStandardHeaders:
    async def test_accept_and_user_agent_are_sent(self):
        async with (
            Recorder(CARDS) as server,
            PayoutClient(MERCHANT, SECRET, api_url=server.url) as client,
        ):
            await client.get_cards()

        (req,) = server.requests
        assert req["headers"]["Accept"] == "application/json"
        assert req["headers"]["User-Agent"].startswith("aioplatega/")
