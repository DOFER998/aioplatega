"""Every client convenience method dispatches the right method object.

The client's job is to build a method and hand it to the session; these check
that binding rather than the HTTP layer, which is covered elsewhere.
"""

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
from aioplatega.types import PaymentDetails

TID = "12345678-1234-5678-1234-567812345678"
SID = "11111111-1111-1111-1111-111111111111"
DETAILS = PaymentDetails(amount=100.0, currency="RUB")


@pytest.mark.parametrize(
    ("call", "expected"),
    [
        (lambda c: c.create_payment_link(payment_details=DETAILS), CreatePaymentLink),
        (lambda c: c.get_h2h_qr(TID), GetH2HQr),
        (lambda c: c.get_balances(), GetBalances),
        (lambda c: c.check_cancel_supported(TID), CheckCancelSupported),
        (lambda c: c.cancel_transaction(TID), CancelTransaction),
        (lambda c: c.export_transactions_csv(), ExportTransactionsCsv),
        (lambda c: c.export_transactions_excel(), ExportTransactionsExcel),
        (lambda c: c.export_transactions_json(), ExportTransactionsJson),
        (lambda c: c.create_subscription(payment_details=DETAILS), CreateSubscription),
        (lambda c: c.get_subscription(SID), GetSubscription),
        (lambda c: c.list_subscriptions(), ListSubscriptions),
        (lambda c: c.cancel_subscription(SID), CancelSubscription),
    ],
)
async def test_dispatches_expected_method(client, mock_session, call, expected):
    await call(client)
    (_, _, method) = mock_session.calls[0]
    assert isinstance(method, expected)


class TestArgumentsReachTheMethod:
    async def test_payment_link_carries_metadata(self, client, mock_session):
        await client.create_payment_link(payment_details=DETAILS, metadata={"orderId": "42"})
        (_, _, method) = mock_session.calls[0]
        assert method.metadata == {"orderId": "42"}

    async def test_export_filters_are_forwarded(self, client, mock_session):
        await client.export_transactions_csv(statuses=["CONFIRMED"], time_zone_id="Europe/Moscow")
        (_, _, method) = mock_session.calls[0]
        assert method.statuses == ["CONFIRMED"]
        assert method.time_zone_id == "Europe/Moscow"

    async def test_subscription_list_filters_are_forwarded(self, client, mock_session):
        await client.list_subscriptions(status="Active", page=2, size=50)
        (_, _, method) = mock_session.calls[0]
        assert method.status == "Active"
        assert method.page == 2
        assert method.size == 50

    async def test_subscription_description_is_forwarded(self, client, mock_session):
        await client.create_subscription(payment_details=DETAILS, description="Premium")
        (_, _, method) = mock_session.calls[0]
        assert method.description == "Premium"


class TestInvalidIdentifiersAreRejectedLocally:
    @pytest.mark.parametrize(
        "call",
        [
            lambda c: c.get_h2h_qr("nope"),
            lambda c: c.check_cancel_supported("nope"),
            lambda c: c.cancel_transaction("nope"),
            lambda c: c.get_subscription("nope"),
            lambda c: c.cancel_subscription("nope"),
        ],
    )
    async def test_bad_uuid_raises_before_any_request(self, client, mock_session, call):
        from aioplatega.exceptions import PlategaValidationError

        with pytest.raises(PlategaValidationError):
            await call(client)
        assert mock_session.calls == []
