"""Coverage for the endpoints added to match docs.platega.io.

Each case pins the URL, HTTP verb and payload shape against the published
specification, since those are what a typo silently breaks.
"""

from uuid import UUID

import pytest

from aioplatega.methods import (
    CancelSubscription,
    CancelTransaction,
    CheckCancelSupported,
    CreatePaymentLink,
    CreateSubscription,
    ExportTransactionsCsv,
    ExportTransactionsExcel,
    ExportTransactionsJson,
    GetBalances,
    GetH2HQr,
    GetSubscription,
    ListSubscriptions,
)
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.types import (
    BalancesResponse,
    CancelSupportedResponse,
    PaymentDetails,
    SubscriptionListResponse,
    TransactionExportResponse,
)
from tests.factories import MERCHANT_ID, SUBSCRIPTION_ID, TRANSACTION_ID

TID = TRANSACTION_ID
SID = SUBSCRIPTION_ID
MERCHANT = MERCHANT_ID


@pytest.fixture
def session():
    return AiohttpSession()


@pytest.mark.parametrize(
    ("method_cls", "verb", "path"),
    [
        (CreatePaymentLink, "POST", "/v2/transaction/process"),
        (GetH2HQr, "GET", "/h2h/{transaction_id}"),
        (GetBalances, "GET", "/balance/all"),
        (CheckCancelSupported, "GET", "/transaction/{transaction_id}/cancel-supported"),
        (CancelTransaction, "POST", "/transaction/{transaction_id}/cancel"),
        (ExportTransactionsCsv, "POST", "/transaction/export/csv"),
        (ExportTransactionsExcel, "POST", "/transaction/export/excel"),
        (ExportTransactionsJson, "POST", "/transaction/export/json"),
        (CreateSubscription, "POST", "/transaction/process"),
        (GetSubscription, "GET", "/subscription/{subscription_id}"),
        (ListSubscriptions, "GET", "/subscription"),
        (CancelSubscription, "POST", "/subscription/{subscription_id}/cancel"),
    ],
)
def test_endpoint_binding(method_cls, verb, path):
    assert method_cls.__http_method__ == verb
    assert method_cls.__api_method__ == path


def test_v2_path_keeps_its_leading_slash(session):
    """Without it the base URL and the path would concatenate into one token."""
    method = CreatePaymentLink(payment_details=PaymentDetails(amount=10.0, currency="RUB"))
    url, _ = session._build_url(method)
    assert url == "https://app.platega.io/v2/transaction/process"


class TestPathParameters:
    @pytest.mark.parametrize(
        ("method", "expected"),
        [
            (lambda: GetH2HQr(transaction_id=UUID(TID)), f"/h2h/{TID}"),
            (
                lambda: CheckCancelSupported(transaction_id=UUID(TID)),
                f"/transaction/{TID}/cancel-supported",
            ),
            (lambda: CancelTransaction(transaction_id=UUID(TID)), f"/transaction/{TID}/cancel"),
            (lambda: GetSubscription(subscription_id=UUID(SID)), f"/subscription/{SID}"),
            (
                lambda: CancelSubscription(subscription_id=UUID(SID)),
                f"/subscription/{SID}/cancel",
            ),
        ],
    )
    def test_id_lands_in_the_path_and_not_the_payload(self, session, method, expected):
        built = method()
        url, consumed = session._build_url(built)
        assert url == f"https://app.platega.io{expected}"
        assert session._build_payload(built, consumed) == {}


class TestSubscriptions:
    def test_create_defaults_to_the_documented_method_id(self):
        """The docs say "always 6"; it is not a PaymentMethodInt member."""
        from aioplatega.enums import SubscriptionInterval
        from aioplatega.types import SubscriptionPaymentDetails

        method = CreateSubscription(
            payment_details=SubscriptionPaymentDetails(
                amount=100, currency="RUB", interval=SubscriptionInterval.MONTH
            )
        )
        payload = method.model_dump(by_alias=True, exclude_none=True)
        assert payload["paymentMethod"] == 6

    def test_list_filters_use_documented_aliases(self):
        method = ListSubscriptions(status="Active", from_date="2026-01-01", to_date="2026-02-01")
        payload = method.model_dump(by_alias=True, exclude_none=True)
        assert payload == {"status": "Active", "from": "2026-01-01", "to": "2026-02-01"}

    def test_list_response_parses_the_documented_example(self):
        parsed = SubscriptionListResponse.model_validate(
            {
                "items": [
                    {
                        "id": SID,
                        "status": 4,
                        "amount": 100,
                        "currencyCode": "RUB",
                        "intervalUnit": 3,
                        "intervalCount": 1,
                    }
                ],
                "total": 1,
                "page": 0,
                "size": 20,
            }
        )
        assert parsed.total == 1
        assert parsed.items[0].currency_code == "RUB"
        assert parsed.items[0].status == 4

    def test_status_tolerates_both_shapes(self):
        """The list response returns status as a number, the detail one as a word."""
        from aioplatega.types import Subscription

        assert Subscription.model_validate({"status": 4}).status == 4
        assert Subscription.model_validate({"status": "Active"}).status == "Active"

    def test_interval_unit_tolerates_both_shapes(self):
        """The vendor returns a number in one response and a word in another."""
        from aioplatega.types import Subscription

        assert Subscription.model_validate({"intervalUnit": 3}).interval_unit == 3
        assert Subscription.model_validate({"intervalUnit": "Month"}).interval_unit == "Month"


class TestExports:
    def test_filters_use_documented_aliases(self):
        method = ExportTransactionsCsv(
            statuses=["CONFIRMED"],
            payment_methods=["SBPQR"],
            from_date="2026-01-01",
            to_date="2026-02-01",
            time_zone_id="Europe/Moscow",
        )
        assert method.model_dump(by_alias=True, exclude_none=True) == {
            "statuses": ["CONFIRMED"],
            "paymentMethods": ["SBPQR"],
            "from": "2026-01-01",
            "to": "2026-02-01",
            "timeZoneId": "Europe/Moscow",
        }

    def test_json_export_parses_the_documented_example(self):
        parsed = TransactionExportResponse.model_validate(
            [
                {
                    "recordId": "486c22ef-3524-4a1c-9740-3fe8c3e859d9",
                    "createdAt": "2026-06-15 13:44:13",
                    "amount": 1150,
                    "currencyCode": "RUB",
                    "status": "CANCELED",
                    "paymentMethod": "SBPQR",
                    "description": "1234",
                    "payload": "",
                }
            ]
        )
        assert len(parsed) == 1
        assert parsed[0].record_id == "486c22ef-3524-4a1c-9740-3fe8c3e859d9"


class TestBareArrayResponses:
    def test_balances_parse_the_documented_example(self):
        parsed = BalancesResponse.model_validate(
            [
                {"amount": 15000.50, "currency": "RUB"},
                {"amount": 200.00, "currency": "USDT", "frozenBalance": 500.00},
            ]
        )
        assert len(parsed) == 2
        assert [b.currency for b in parsed] == ["RUB", "USDT"]
        assert parsed[1].frozen_balance == 500.00

    def test_frozen_balance_alias_is_wired(self):
        assert BalancesResponse.model_validate([{"frozenBalance": 1.0}])[0].frozen_balance == 1.0


class TestCancellation:
    def test_cancel_supported_parses_the_documented_example(self):
        parsed = CancelSupportedResponse.model_validate(
            {
                "supported": True,
                "totalDeductUsdt": 0.01236094,
                "penaltyNativeAmount": None,
                "penaltyNativeCurrency": None,
                "penaltyUsdt": None,
                "penaltyConversionRate": None,
                "blockReason": None,
            }
        )
        assert parsed.supported is True
        assert parsed.total_deduct_usdt == 0.01236094

    def test_unsupported_carries_a_reason(self):
        parsed = CancelSupportedResponse.model_validate(
            {"supported": False, "blockReason": "Insufficient balance"}
        )
        assert parsed.supported is False
        assert parsed.block_reason == "Insufficient balance"


class TestCallbackTypes:
    def test_subscription_charge_callback_uses_pascal_case(self):
        from aioplatega.types import SubscriptionChargeCallback

        parsed = SubscriptionChargeCallback.model_validate(
            {
                "Id": TID,
                "Amount": 100,
                "Currency": "RUB",
                "Status": "CONFIRMED",
                "PaymentMethod": 6,
                "Payload": "x",
                "SubscriptionId": SID,
                "NextChargeAt": "2026-08-09T09:10:00Z",
            }
        )
        assert parsed.subscription_id == SID
        assert parsed.status == "CONFIRMED"

    def test_subscription_status_callback(self):
        from aioplatega.types import SubscriptionStatusCallback

        parsed = SubscriptionStatusCallback.model_validate(
            {"Id": SID, "Status": "SUBSCRIPTION_CANCELLED"}
        )
        assert parsed.id == SID
        assert parsed.status == "SUBSCRIPTION_CANCELLED"


class TestDocumentedDivergences:
    def test_transaction_status_reads_the_vendors_mechant_id_typo(self):
        from aioplatega.types import TransactionStatusResponse

        parsed = TransactionStatusResponse.model_validate({"mechantId": TID})
        assert str(parsed.merchant_id) == TID

    def test_correct_spelling_still_works(self):
        from aioplatega.types import TransactionStatusResponse

        parsed = TransactionStatusResponse.model_validate({"merchantId": TID})
        assert str(parsed.merchant_id) == TID

    def test_create_transaction_accepts_metadata(self):
        from aioplatega.enums import PaymentMethodInt
        from aioplatega.methods import CreateTransaction

        method = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=1.0, currency="RUB"),
            metadata={"orderId": "42"},
        )
        assert method.model_dump(by_alias=True, exclude_none=True)["metadata"] == {"orderId": "42"}
