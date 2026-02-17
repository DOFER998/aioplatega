from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from aioplatega.enums import PaymentMethodInt, PaymentStatus
from aioplatega.types import (
    CallbackPayload,
    ConversionItem,
    ConversionsResponse,
    CreateTransactionRequest,
    CreateTransactionResponse,
    PaymentDetails,
    RateResponse,
    TransactionStatusResponse,
)


class TestPlategaObject:
    def test_frozen(self):
        obj = PaymentDetails(amount=100.0, currency="RUB")
        with pytest.raises(ValidationError):
            obj.amount = 200.0  # type: ignore[misc]

    def test_extra_fields_allowed(self):
        obj = PaymentDetails(amount=100.0, currency="RUB", extra_field="test")
        assert obj.extra_field == "test"  # type: ignore[attr-defined]


class TestPaymentDetails:
    def test_construction(self):
        pd = PaymentDetails(amount=150.5, currency="USD")
        assert pd.amount == 150.5
        assert pd.currency == "USD"

    def test_serialization(self):
        pd = PaymentDetails(amount=100.0, currency="RUB")
        data = pd.model_dump()
        assert data == {"amount": 100.0, "currency": "RUB"}


class TestCallbackPayload:
    def test_construction(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        cp = CallbackPayload(
            id=uid,
            amount=100.0,
            currency="RUB",
            status="CONFIRMED",
            payment_method=2,
        )
        assert cp.id == uid
        assert cp.amount == 100.0
        assert cp.payment_method == 2

    def test_alias_serialization(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        cp = CallbackPayload(
            id=uid,
            amount=100.0,
            currency="RUB",
            status="CONFIRMED",
            payment_method=2,
        )
        data = cp.model_dump(by_alias=True)
        assert "paymentMethod" in data

    def test_from_alias(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        cp = CallbackPayload(
            id=uid,
            amount=100.0,
            currency="RUB",
            status="CONFIRMED",
            paymentMethod=2,
        )
        assert cp.payment_method == 2

    def test_optional_payload(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        cp = CallbackPayload(
            id=uid,
            amount=100.0,
            currency="RUB",
            status="CONFIRMED",
            payment_method=2,
            payload="custom-data",
        )
        assert cp.payload == "custom-data"


class TestCreateTransactionRequest:
    def test_construction(self):
        req = CreateTransactionRequest(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )
        assert req.payment_method == 2
        assert req.payment_details.amount == 100.0

    def test_alias_dump(self):
        req = CreateTransactionRequest(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )
        data = req.model_dump(by_alias=True)
        assert "paymentMethod" in data
        assert "paymentDetails" in data


class TestCreateTransactionResponse:
    def test_construction(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        resp = CreateTransactionResponse(
            transaction_id=uid,
            status=PaymentStatus.PENDING,
        )
        assert resp.transaction_id == uid
        assert resp.status == "PENDING"

    def test_alias_serialization(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        resp = CreateTransactionResponse(
            transaction_id=uid,
            status=PaymentStatus.PENDING,
        )
        data = resp.model_dump(by_alias=True)
        assert "transactionId" in data

    def test_with_all_fields(self):
        tid = UUID("12345678-1234-5678-1234-567812345678")
        mid = UUID("87654321-4321-8765-4321-876543218765")
        resp = CreateTransactionResponse(
            transaction_id=tid,
            status=PaymentStatus.PENDING,
            payment_method="SBP_QR",
            redirect="https://pay.example.com",
            return_url="https://merchant.com/return",
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            expires_in="300",
            merchant_id=mid,
            usdt_rate=95.5,
        )
        assert resp.redirect == "https://pay.example.com"
        assert resp.merchant_id == mid
        assert resp.usdt_rate == 95.5


class TestTransactionStatusResponse:
    def test_all_optional(self):
        resp = TransactionStatusResponse()
        assert resp.id is None
        assert resp.status is None
        assert resp.payment_details is None

    def test_with_data(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        resp = TransactionStatusResponse(
            id=uid,
            status=PaymentStatus.CONFIRMED,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )
        assert resp.id == uid
        assert resp.status == "CONFIRMED"


class TestRateResponse:
    def test_construction(self):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        rate = RateResponse(
            payment_method=2,
            currency_from="RUB",
            currency_to="USDT",
            rate=0.0105,
            updated_at=dt,
        )
        assert rate.rate == 0.0105
        assert rate.currency_from == "RUB"

    def test_alias_dump(self):
        rate = RateResponse(payment_method=2, rate=0.01)
        data = rate.model_dump(by_alias=True)
        assert "paymentMethod" in data
        assert "currencyFrom" in data


class TestConversionItem:
    def test_construction(self):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        item = ConversionItem(
            id=1,
            amount=100.0,
            currency="RUB",
            status="completed",
            created_at=dt,
        )
        assert item.id == 1
        assert item.amount == 100.0

    def test_alias_dump(self):
        item = ConversionItem(id=1, amount=50.0)
        data = item.model_dump(by_alias=True)
        assert "createdAt" in data


class TestConversionsResponse:
    def test_empty(self):
        resp = ConversionsResponse()
        assert resp.content == []
        assert resp.total_elements == 0
        assert resp.total_pages == 0
        assert resp.page == 0
        assert resp.size == 0

    def test_with_items(self):
        items = [
            ConversionItem(id=1, amount=100.0),
            ConversionItem(id=2, amount=200.0),
        ]
        resp = ConversionsResponse(
            content=items,
            total_elements=2,
            total_pages=1,
            page=0,
            size=20,
        )
        assert len(resp.content) == 2
        assert resp.total_elements == 2

    def test_alias_dump(self):
        resp = ConversionsResponse()
        data = resp.model_dump(by_alias=True)
        assert "totalElements" in data
        assert "totalPages" in data
