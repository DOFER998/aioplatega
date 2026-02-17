from uuid import UUID

from aioplatega.enums import PaymentMethodInt
from aioplatega.methods import (
    CreateTransaction,
    GetConversions,
    GetRate,
    GetTransactionStatus,
)
from aioplatega.methods.base import PlategaMethod
from aioplatega.types import (
    ConversionsResponse,
    CreateTransactionResponse,
    PaymentDetails,
    RateResponse,
    TransactionStatusResponse,
)


class TestPlategaMethodBase:
    def test_class_vars_declared_in_annotations(self):
        annotations = PlategaMethod.__annotations__
        assert "__api_method__" in annotations
        assert "__http_method__" in annotations
        assert "__returning__" in annotations


class TestCreateTransaction:
    def test_class_vars(self):
        assert CreateTransaction.__api_method__ == "/transaction/process"
        assert CreateTransaction.__http_method__ == "POST"
        assert CreateTransaction.__returning__ is CreateTransactionResponse

    def test_construction(self):
        method = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )
        assert method.payment_method == 2
        assert method.payment_details.amount == 100.0

    def test_dump_by_alias(self):
        method = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            description="Test payment",
        )
        data = method.model_dump(by_alias=True, exclude_none=True)
        assert "paymentMethod" in data
        assert "paymentDetails" in data
        assert data["paymentMethod"] == 2

    def test_optional_fields_excluded(self):
        method = CreateTransaction(
            payment_method=PaymentMethodInt.CARDS_RUB,
            payment_details=PaymentDetails(amount=50.0, currency="USD"),
        )
        data = method.model_dump(by_alias=True, exclude_none=True)
        assert "return" not in data
        assert "failedUrl" not in data
        assert "payload" not in data


class TestGetTransactionStatus:
    def test_class_vars(self):
        assert GetTransactionStatus.__api_method__ == "/transaction/{transaction_id}"
        assert GetTransactionStatus.__http_method__ == "GET"
        assert GetTransactionStatus.__returning__ is TransactionStatusResponse

    def test_construction(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        method = GetTransactionStatus(transaction_id=uid)
        assert method.transaction_id == uid

    def test_dump_by_alias(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        method = GetTransactionStatus(transaction_id=uid)
        data = method.model_dump(by_alias=True, exclude_none=True)
        assert "transactionId" in data


class TestGetRate:
    def test_class_vars(self):
        assert GetRate.__api_method__ == "/rates/payment_method_rate"
        assert GetRate.__http_method__ == "GET"
        assert GetRate.__returning__ is RateResponse

    def test_construction(self):
        method = GetRate(
            merchant_id="m-123",
            payment_method=2,
            currency_from="RUB",
            currency_to="USDT",
        )
        assert method.merchant_id == "m-123"
        assert method.payment_method == 2

    def test_dump_by_alias(self):
        method = GetRate(
            merchant_id="m-123",
            payment_method=2,
            currency_from="RUB",
            currency_to="USDT",
        )
        data = method.model_dump(by_alias=True, exclude_none=True)
        assert "merchantId" in data
        assert "paymentMethod" in data
        assert "currencyFrom" in data
        assert "currencyTo" in data


class TestGetConversions:
    def test_class_vars(self):
        assert GetConversions.__api_method__ == "/transaction/balance-unlock-operations"
        assert GetConversions.__http_method__ == "GET"
        assert GetConversions.__returning__ is ConversionsResponse

    def test_construction_defaults(self):
        method = GetConversions()
        assert method.page == 0
        assert method.size == 20
        assert method.from_date is None
        assert method.to_date is None

    def test_construction_with_dates(self):
        method = GetConversions(
            from_date="2025-01-01",
            to_date="2025-01-31",
            page=1,
            size=50,
        )
        assert method.from_date == "2025-01-01"
        assert method.page == 1
        assert method.size == 50

    def test_dump_by_alias(self):
        method = GetConversions(from_date="2025-01-01", to_date="2025-12-31")
        data = method.model_dump(by_alias=True, exclude_none=True)
        assert "from" in data
        assert "to" in data
        assert data["page"] == 0
        assert data["size"] == 20
