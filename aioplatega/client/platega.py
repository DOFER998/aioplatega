from __future__ import annotations

from typing import TypeVar

from aioplatega.enums import PaymentMethodInt
from aioplatega.methods import (
    CreateTransaction,
    GetConversions,
    GetRate,
    GetTransactionStatus,
)
from aioplatega.methods.base import PlategaMethod
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.session.base import BaseSession
from aioplatega.types import (
    ConversionsResponse,
    CreateTransactionResponse,
    PaymentDetails,
    RateResponse,
    TransactionStatusResponse,
)

T = TypeVar("T")


class Platega:
    """Async client for the Platega payment API.

    Usage::

        async with Platega(merchant_id="...", secret="...") as client:
            result = await client.create_transaction(...)
    """

    def __init__(
        self,
        merchant_id: str,
        secret: str,
        session: BaseSession | None = None,
    ) -> None:
        """Initialize the Platega client.

        Args:
            merchant_id: Your Platega merchant identifier.
            secret: Your Platega secret key.
            session: Optional custom session. If not provided, an
                :class:`~aioplatega.session.aiohttp.AiohttpSession` is created automatically.
        """
        self._merchant_id = merchant_id
        self._secret = secret
        self._session = session
        self._owns_session = session is None

    def _get_session(self) -> BaseSession:
        if self._session is None:
            self._session = AiohttpSession()
            self._owns_session = True
        return self._session

    async def __call__(self, method: PlategaMethod[T]) -> T:
        """Dispatch a method object (aiogram-style command pattern)."""
        session = self._get_session()
        return await session.make_request(  # type: ignore[no-any-return]
            merchant_id=self._merchant_id,
            secret=self._secret,
            method=method,
        )

    async def create_transaction(
        self,
        *,
        payment_method: PaymentMethodInt,
        payment_details: PaymentDetails,
        description: str | None = None,
        return_url: str | None = None,
        failed_url: str | None = None,
        payload: str | None = None,
    ) -> CreateTransactionResponse:
        """Create a new payment transaction.

        Args:
            payment_method: Payment method identifier (e.g. ``PaymentMethodInt.SBP_QR``).
            payment_details: Amount and currency for the payment.
            description: Optional human-readable description.
            return_url: URL to redirect the user after successful payment.
            failed_url: URL to redirect the user after failed payment.
            payload: Arbitrary string passed through to the callback.

        Returns:
            Response containing the transaction ID, status, and redirect URL.
        """
        return await self(
            CreateTransaction(
                payment_method=payment_method,
                payment_details=payment_details,
                description=description,
                return_url=return_url,
                failed_url=failed_url,
                payload=payload,
            )
        )

    async def get_transaction_status(
        self,
        transaction_id: str,
    ) -> TransactionStatusResponse:
        """Get the current status of a transaction.

        Args:
            transaction_id: UUID of the transaction to query.

        Returns:
            Full transaction details including status and payment info.
        """
        return await self(
            GetTransactionStatus(transaction_id=transaction_id),  # type: ignore[arg-type]
        )

    async def get_rate(
        self,
        *,
        payment_method: int,
        currency_from: str,
        currency_to: str,
    ) -> RateResponse:
        """Get the current exchange rate for a payment method.

        Args:
            payment_method: Payment method identifier (int value).
            currency_from: Source currency code (e.g. ``"USDT"``).
            currency_to: Target currency code (e.g. ``"RUB"``).

        Returns:
            Current rate and last update timestamp.
        """
        return await self(
            GetRate(
                merchant_id=self._merchant_id,
                payment_method=payment_method,
                currency_from=currency_from,
                currency_to=currency_to,
            )
        )

    async def get_conversions(
        self,
        *,
        from_date: str | None = None,
        to_date: str | None = None,
        page: int = 0,
        size: int = 20,
    ) -> ConversionsResponse:
        """Get a paginated list of balance-unlock (conversion) operations.

        Args:
            from_date: Start date filter (ISO format string).
            to_date: End date filter (ISO format string).
            page: Zero-based page number.
            size: Number of items per page.

        Returns:
            Paginated response with conversion items.
        """
        return await self(
            GetConversions(
                from_date=from_date,
                to_date=to_date,
                page=page,
                size=size,
            )
        )

    async def close(self) -> None:
        """Close the underlying HTTP session and release resources."""
        if self._session is not None and self._owns_session:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> Platega:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
