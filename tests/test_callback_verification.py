"""Verifying an incoming callback.

Platega authenticates callbacks by echoing the merchant's own credentials
back in the X-MerchantId and X-Secret headers — there is no signature. The
receiver has to compare them, which makes a constant-time comparison the
difference between a safe check and one that leaks the secret.
"""

import json

import pytest

from aioplatega import Platega
from aioplatega.callback import verify_callback
from aioplatega.exceptions import PlategaError, PlategaValidationError
from aioplatega.types import CallbackPayload, SubscriptionChargeCallback

MERCHANT = "29ef0000-0000-0000-0000-000000000000"
SECRET = "test-secret"
TID = "12345678-1234-5678-1234-567812345678"

BODY = {
    "id": TID,
    "amount": 100.0,
    "currency": "RUB",
    "status": "CONFIRMED",
    "paymentMethod": 2,
    "payload": "order-42",
}
HEADERS = {"X-MerchantId": MERCHANT, "X-Secret": SECRET}


def raw(body: dict[str, object] | None = None) -> str:
    return json.dumps(body if body is not None else BODY)


class TestAccepted:
    def test_returns_the_parsed_payload(self):
        parsed = verify_callback(HEADERS, raw(), merchant_id=MERCHANT, secret=SECRET)
        assert isinstance(parsed, CallbackPayload)
        assert str(parsed.id) == TID
        assert parsed.payload == "order-42"

    def test_accepts_bytes(self):
        parsed = verify_callback(HEADERS, raw().encode(), merchant_id=MERCHANT, secret=SECRET)
        assert parsed.amount == 100.0

    @pytest.mark.parametrize("key", ["x-merchantid", "X-MERCHANTID", "X-MerchantId"])
    def test_header_lookup_is_case_insensitive(self, key):
        headers = {key: MERCHANT, "x-secret": SECRET}
        assert verify_callback(headers, raw(), merchant_id=MERCHANT, secret=SECRET)

    def test_hyphenated_merchant_header_spelling_is_accepted(self):
        """Some stacks normalise the header to X-Merchant-Id."""
        headers = {"X-Merchant-Id": MERCHANT, "X-Secret": SECRET}
        assert verify_callback(headers, raw(), merchant_id=MERCHANT, secret=SECRET)

    def test_chargebacked_is_accepted(self):
        body = {**BODY, "status": "CHARGEBACKED"}
        parsed = verify_callback(HEADERS, raw(body), merchant_id=MERCHANT, secret=SECRET)
        assert parsed.status == "CHARGEBACKED"

    def test_subscription_callback_model_can_be_supplied(self):
        body = {
            "Id": TID,
            "Amount": 100,
            "Currency": "RUB",
            "Status": "CONFIRMED",
            "PaymentMethod": 6,
            "SubscriptionId": TID,
            "NextChargeAt": "2026-08-09T09:10:00Z",
        }
        parsed = verify_callback(
            HEADERS,
            raw(body),
            merchant_id=MERCHANT,
            secret=SECRET,
            model=SubscriptionChargeCallback,
        )
        assert parsed.subscription_id == TID


class TestRejected:
    @pytest.mark.parametrize(
        "headers",
        [
            {"X-MerchantId": MERCHANT, "X-Secret": "wrong"},
            {"X-MerchantId": "wrong", "X-Secret": SECRET},
            {"X-MerchantId": MERCHANT},
            {"X-Secret": SECRET},
            {},
            {"X-MerchantId": "", "X-Secret": ""},
        ],
    )
    def test_bad_credentials(self, headers):
        with pytest.raises(PlategaValidationError):
            verify_callback(headers, raw(), merchant_id=MERCHANT, secret=SECRET)

    def test_empty_body(self):
        with pytest.raises(PlategaValidationError, match="empty"):
            verify_callback(HEADERS, "", merchant_id=MERCHANT, secret=SECRET)

    def test_malformed_json(self):
        with pytest.raises(PlategaValidationError, match="JSON"):
            verify_callback(HEADERS, "not json", merchant_id=MERCHANT, secret=SECRET)

    def test_missing_required_field(self):
        body = {k: v for k, v in BODY.items() if k != "currency"}
        with pytest.raises(PlategaValidationError):
            verify_callback(HEADERS, raw(body), merchant_id=MERCHANT, secret=SECRET)

    def test_rejection_is_a_platega_error(self):
        with pytest.raises(PlategaError):
            verify_callback({}, raw(), merchant_id=MERCHANT, secret=SECRET)

    def test_credentials_are_compared_in_constant_time(self):
        """A plain == leaks the secret one byte at a time to a caller who can time it."""
        import inspect

        from aioplatega import callback

        assert "compare_digest" in inspect.getsource(callback)


class TestClientConvenience:
    def test_client_verifies_with_its_own_credentials(self):
        client = Platega(merchant_id=MERCHANT, secret=SECRET)
        parsed = client.verify_callback(HEADERS, raw())
        assert str(parsed.id) == TID

    def test_client_rejects_a_foreign_secret(self):
        client = Platega(merchant_id=MERCHANT, secret="another")
        with pytest.raises(PlategaValidationError):
            client.verify_callback(HEADERS, raw())
