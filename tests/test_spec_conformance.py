"""Conformance with the two published specifications.

Platega documents its API in two places that do not agree: the current
Apidog site at docs.platega.io and an older GitBook. Where they differ the
SDK has to accept the union, because the API answers with values from both.
"""

import pytest

from aioplatega.enums import PaymentMethodInt, PaymentStatus
from aioplatega.types import (
    CreateTransactionResponse,
    H2HQrResponse,
    TransactionStatusResponse,
)

TID = "12345678-1234-5678-1234-567812345678"


class TestPaymentStatus:
    @pytest.mark.parametrize(
        "value",
        ["PENDING", "CONFIRMED", "CANCELED", "CHARGEBACKED", "EXPIRED", "FAILED"],
    )
    def test_documented_value_is_a_member(self, value):
        assert PaymentStatus(value).value == value

    @pytest.mark.parametrize("value", ["EXPIRED", "FAILED"])
    def test_gitbook_only_statuses_parse(self, value):
        """A 15-minute payment window makes EXPIRED a routine outcome."""
        parsed = TransactionStatusResponse.model_validate({"id": TID, "status": value})
        assert parsed.status == value

    def test_unknown_status_does_not_break_the_response(self):
        """An undocumented value must not make the whole payload unparseable."""
        parsed = TransactionStatusResponse.model_validate({"id": TID, "status": "SOMETHING_NEW"})
        assert parsed.status == "SOMETHING_NEW"

    def test_create_response_tolerates_unknown_status_too(self):
        parsed = CreateTransactionResponse.model_validate(
            {"transactionId": TID, "status": "SOMETHING_NEW"}
        )
        assert parsed.status == "SOMETHING_NEW"

    def test_known_status_still_compares_to_the_enum(self):
        parsed = TransactionStatusResponse.model_validate({"id": TID, "status": "CONFIRMED"})
        assert parsed.status == PaymentStatus.CONFIRMED


class TestPaymentMethodInt:
    @pytest.mark.parametrize(
        ("value", "name"),
        [
            (2, "SBP_QR"),
            (3, "ERIP"),
            (10, "CARDS_RUB"),
            (11, "CARD_ACQUIRING"),
            (12, "INTERNATIONAL_ACQUIRING"),
            (13, "CRYPTO"),
        ],
    )
    def test_documented_methods(self, value, name):
        assert PaymentMethodInt(value).name == name

    def test_cards_rub_is_documented_not_deprecated(self):
        """10 is absent from the Apidog enum but named in the GitBook table."""
        doc = PaymentMethodInt.CARDS_RUB.__doc__ or ""
        assert "MIR" in doc or "GitBook" in doc


class TestH2HResponse:
    def test_apidog_shape(self):
        parsed = H2HQrResponse.model_validate({"amount": 136.12, "qr": "https://qr.nspk.ru/x"})
        assert parsed.amount == 136.12
        assert parsed.qr == "https://qr.nspk.ru/x"

    def test_gitbook_p2p_requisites_shape(self):
        """The older docs return bank requisites from the same endpoint."""
        parsed = H2HQrResponse.model_validate(
            {
                "accountNumber": "2200 7004 0146 3121",
                "maskedAccountNumber": "2200 7004 0146 3121",
                "accountName": "Jhon M",
                "method": "tinkoff",
                "amount": 2000,
            }
        )
        assert parsed.account_number == "2200 7004 0146 3121"
        assert parsed.account_name == "Jhon M"
        assert parsed.method == "tinkoff"
        assert parsed.amount == 2000


class TestPaymentMethodIsNotAClosedSet:
    """The enum names the documented methods; it is not the list of valid ones.

    The GitBook states that methods 1 through 9 are P2P, and a merchant is
    enabled for whichever ones their contract covers. Rejecting an id merely
    because it is unnamed here would lock those merchants out entirely.
    """

    @pytest.mark.parametrize("method", [1, 4, 5, 6, 7, 8, 9, 99])
    def test_unnamed_method_id_is_accepted(self, method):
        from aioplatega.methods import CreateTransaction
        from aioplatega.types import PaymentDetails

        built = CreateTransaction(
            payment_method=method,
            payment_details=PaymentDetails(amount=1000.0, currency="RUB"),
        )
        assert built.model_dump(by_alias=True)["paymentMethod"] == method

    def test_named_member_still_serializes_to_its_value(self):
        from aioplatega.methods import CreateTransaction
        from aioplatega.types import PaymentDetails

        built = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=1000.0, currency="RUB"),
        )
        assert built.model_dump(by_alias=True)["paymentMethod"] == 2

    async def test_client_accepts_a_bare_int(self, client, mock_session):
        from aioplatega.types import PaymentDetails

        await client.create_transaction(
            payment_method=5,
            payment_details=PaymentDetails(amount=1000.0, currency="RUB"),
        )
        (_, _, method) = mock_session.calls[0]
        assert method.payment_method == 5

    def test_request_type_matches_the_method(self):
        from aioplatega.types import CreateTransactionRequest, PaymentDetails

        built = CreateTransactionRequest(
            payment_method=7,
            payment_details=PaymentDetails(amount=1000.0, currency="RUB"),
        )
        assert built.payment_method == 7


class TestCallbackStatusIsOpen:
    """The callback schema names two statuses; the same page's prose adds a third."""

    @pytest.mark.parametrize("status", ["CONFIRMED", "CANCELED", "CHARGEBACKED"])
    def test_documented_callback_statuses_parse(self, status):
        from aioplatega.types import CallbackPayload

        parsed = CallbackPayload.model_validate(
            {
                "id": TID,
                "amount": 100.0,
                "currency": "RUB",
                "status": status,
                "paymentMethod": 2,
            }
        )
        assert parsed.status == status

    def test_callback_without_payload_field_parses(self):
        """The schema omits `payload`; only the endpoint page lists it."""
        from aioplatega.types import CallbackPayload

        parsed = CallbackPayload.model_validate(
            {
                "id": TID,
                "amount": 100.0,
                "currency": "RUB",
                "status": "CONFIRMED",
                "paymentMethod": 2,
            }
        )
        assert parsed.payload is None


class TestMetadataIsDocumented:
    """metadata.userId is an operational requirement, not a nicety."""

    def test_metadata_reaches_the_request_body(self):
        from aioplatega.methods import CreateTransaction
        from aioplatega.types import PaymentDetails

        built = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=500.0, currency="RUB"),
            metadata={"userId": "u-1"},
        )
        assert built.model_dump(by_alias=True, exclude_none=True)["metadata"] == {"userId": "u-1"}

    def test_payment_link_carries_metadata_too(self):
        from aioplatega.methods import CreatePaymentLink
        from aioplatega.types import PaymentDetails

        built = CreatePaymentLink(
            payment_details=PaymentDetails(amount=500.0, currency="RUB"),
            metadata={"userId": "u-1"},
        )
        assert built.model_dump(by_alias=True, exclude_none=True)["metadata"] == {"userId": "u-1"}

    def test_requirement_is_stated_where_callers_will_see_it(self):
        from aioplatega import Platega
        from aioplatega.types import CreateTransactionRequest

        assert "userId" in (CreateTransactionRequest.__doc__ or "")
        assert "userId" in (Platega.create_transaction.__doc__ or "")
        assert "userId" in (Platega.create_payment_link.__doc__ or "")


class TestSubscriptionInterval:
    """The mapping is documented, nested inside paymentDetails on create."""

    @pytest.mark.parametrize(
        ("value", "name"),
        [("1", "DAY"), ("2", "WEEK"), ("3", "MONTH"), ("4", "YEAR")],
    )
    def test_documented_mapping(self, value, name):
        from aioplatega.enums import SubscriptionInterval

        assert SubscriptionInterval(value).name == name


class TestSubscriptionPaymentDetails:
    """`interval` is required on the subscription create body, not optional."""

    def test_interval_is_required(self):
        from pydantic import ValidationError

        from aioplatega.types import SubscriptionPaymentDetails

        with pytest.raises(ValidationError):
            SubscriptionPaymentDetails(amount=500, currency="RUB")

    def test_body_matches_the_documented_example(self):
        from aioplatega.enums import SubscriptionInterval
        from aioplatega.methods import CreateSubscription
        from aioplatega.types import SubscriptionPaymentDetails

        built = CreateSubscription(
            payment_details=SubscriptionPaymentDetails(
                amount=500,
                currency="RUB",
                interval=SubscriptionInterval.MONTH,
            ),
            description="Premium подписка",
        )
        assert built.model_dump(mode="json", by_alias=True, exclude_none=True) == {
            "paymentMethod": 6,
            "paymentDetails": {"amount": 500, "currency": "RUB", "interval": "3"},
            "description": "Premium подписка",
        }

    async def test_client_sends_the_interval(self, client, mock_session):
        from aioplatega.enums import SubscriptionInterval
        from aioplatega.types import SubscriptionPaymentDetails

        await client.create_subscription(
            payment_details=SubscriptionPaymentDetails(
                amount=100,
                currency="RUB",
                interval=SubscriptionInterval.WEEK,
            ),
            description="Weekly",
        )
        (_, _, method) = mock_session.calls[0]
        assert method.payment_details.interval == "2"
