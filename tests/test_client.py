from uuid import UUID

import pytest

from aioplatega.client import Platega
from aioplatega.enums import PaymentMethodInt, PaymentStatus
from aioplatega.methods import (
    CreateTransaction,
    GetConversions,
    GetRate,
    GetTransactionStatus,
)
from aioplatega.types import (
    ConversionsResponse,
    CreateTransactionResponse,
    PaymentDetails,
    RateResponse,
    TransactionStatusResponse,
)
from tests.conftest import MockSession


class TestClientDispatch:
    async def test_call_dispatches_to_session(self, client, mock_session):
        mock_session.response = CreateTransactionResponse(
            transaction_id=UUID("12345678-1234-5678-1234-567812345678"),
            status=PaymentStatus.PENDING,
        )

        method = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )
        result = await client(method)

        assert len(mock_session.calls) == 1
        merchant_id, secret, called_method = mock_session.calls[0]
        assert merchant_id == "test-merchant"
        assert secret == "test-secret"
        assert isinstance(called_method, CreateTransaction)
        assert isinstance(result, CreateTransactionResponse)

    async def test_call_propagates_exception(self, client, mock_session):
        mock_session.response = ValueError("test error")

        method = CreateTransaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
        )
        with pytest.raises(ValueError, match="test error"):
            await client(method)


class TestConvenienceMethods:
    async def test_create_transaction(self, client, mock_session):
        expected = CreateTransactionResponse(
            transaction_id=UUID("12345678-1234-5678-1234-567812345678"),
            status=PaymentStatus.PENDING,
        )
        mock_session.response = expected

        result = await client.create_transaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            description="Test",
        )

        assert result is expected
        assert len(mock_session.calls) == 1
        _, _, method = mock_session.calls[0]
        assert isinstance(method, CreateTransaction)

    async def test_get_transaction_status(self, client, mock_session):
        expected = TransactionStatusResponse(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            status=PaymentStatus.CONFIRMED,
        )
        mock_session.response = expected

        result = await client.get_transaction_status(
            "12345678-1234-5678-1234-567812345678",
        )

        assert result is expected
        _, _, method = mock_session.calls[0]
        assert isinstance(method, GetTransactionStatus)

    async def test_get_rate(self, client, mock_session):
        expected = RateResponse(rate=0.0105)
        mock_session.response = expected

        result = await client.get_rate(
            payment_method=2,
            currency_from="RUB",
            currency_to="USDT",
        )

        assert result is expected
        _, _, method = mock_session.calls[0]
        assert isinstance(method, GetRate)
        data = method.model_dump(by_alias=False)
        assert data["merchant_id"] == "test-merchant"

    async def test_get_conversions(self, client, mock_session):
        expected = ConversionsResponse()
        mock_session.response = expected

        result = await client.get_conversions(
            from_date="2025-01-01",
            to_date="2025-01-31",
            page=0,
            size=10,
        )

        assert result is expected
        _, _, method = mock_session.calls[0]
        assert isinstance(method, GetConversions)


class TestClientLifecycle:
    async def test_close_closes_owned_session(self):
        mock = MockSession()
        client = Platega(merchant_id="m", secret="s", session=mock)
        # Session was passed in, so client does NOT own it
        await client.close()
        assert not mock.closed

    async def test_close_closes_auto_created_session(self):
        mock = MockSession()
        client = Platega(merchant_id="m", secret="s")
        # Replace the auto-created session reference
        client._session = mock
        client._owns_session = True
        await client.close()
        assert mock.closed

    async def test_async_context_manager(self, mock_session):
        async with Platega(
            merchant_id="m",
            secret="s",
            session=mock_session,
        ) as client:
            assert client._session is mock_session

    async def test_get_session_creates_aiohttp_session(self):
        client = Platega(merchant_id="m", secret="s")
        session = client._get_session()
        assert session is not None
        assert client._owns_session is True
        await client.close()

    async def test_owns_session_false_when_injected(self):
        mock = MockSession()
        client = Platega(merchant_id="m", secret="s", session=mock)
        assert client._owns_session is False
