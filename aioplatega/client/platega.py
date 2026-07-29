from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import ValidationError

from aioplatega.enums import PaymentMethodInt
from aioplatega.exceptions import PlategaValidationError
from aioplatega.methods import (
    CancelSubscription,
    CancelTransaction,
    CheckCancelSupported,
    CreatePaymentLink,
    CreateSubscription,
    CreateTransaction,
    ExportTransactionsCsv,
    ExportTransactionsExcel,
    ExportTransactionsJson,
    GetBalances,
    GetConversions,
    GetH2HQr,
    GetRate,
    GetSubscription,
    GetTransactionStatus,
    ListSubscriptions,
)
from aioplatega.methods.base import PlategaMethod
from aioplatega.session.aiohttp import AiohttpSession
from aioplatega.session.base import BaseSession
from aioplatega.types import (
    BalancesResponse,
    CancelSubscriptionResponse,
    CancelSupportedResponse,
    CancelTransactionResponse,
    ConversionsResponse,
    CreateSubscriptionResponse,
    CreateTransactionResponse,
    ExportUrlResponse,
    H2HQrResponse,
    PaymentDetails,
    PaymentLinkResponse,
    RateResponse,
    Subscription,
    SubscriptionListResponse,
    TransactionExportResponse,
    TransactionStatusResponse,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


@contextmanager
def _validated() -> Iterator[None]:
    """Translate pydantic's ValidationError into the library's own hierarchy.

    Callers of an SDK should be able to catch :class:`PlategaError` and be done;
    leaking a pydantic type would make them depend on our validation library.
    """
    try:
        yield
    except ValidationError as exc:
        raise PlategaValidationError(str(exc)) from exc


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

    async def __call__[T](self, method: PlategaMethod[T]) -> T:
        """Dispatch a method object (command pattern)."""
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

        Raises:
            PlategaValidationError: If the arguments are not a valid request.
        """
        with _validated():
            method = CreateTransaction(
                payment_method=payment_method,
                payment_details=payment_details,
                description=description,
                return_url=return_url,
                failed_url=failed_url,
                payload=payload,
            )
        return await self(method)

    async def get_transaction_status(
        self,
        transaction_id: str | UUID,
    ) -> TransactionStatusResponse:
        """Get the current status of a transaction.

        Args:
            transaction_id: UUID of the transaction to query, as a
                :class:`~uuid.UUID` or its string form.

        Returns:
            Full transaction details including status and payment info.

        Raises:
            PlategaValidationError: If ``transaction_id`` is not a valid UUID.
        """
        with _validated():
            method = GetTransactionStatus(transaction_id=transaction_id)
        return await self(method)

    async def get_rate(
        self,
        *,
        payment_method: PaymentMethodInt | int,
        currency_from: str,
        currency_to: str,
    ) -> RateResponse:
        """Get the current exchange rate for a payment method.

        Args:
            payment_method: Payment method identifier, e.g.
                ``PaymentMethodInt.SBP_QR``.
            currency_from: Source currency code (e.g. ``"USDT"``).
            currency_to: Target currency code (e.g. ``"RUB"``).

        Returns:
            Current rate and last update timestamp.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.

        .. warning::
           This endpoint does not appear anywhere in the published API
           documentation at https://docs.platega.io. It is kept because
           removing it would break existing callers, but treat it as legacy:
           it may be withdrawn without notice.
        """
        with _validated():
            method = GetRate(
                merchant_id=self._merchant_id,
                payment_method=payment_method,
                currency_from=currency_from,
                currency_to=currency_to,
            )
        return await self(method)

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

        Raises:
            PlategaValidationError: If the arguments are not a valid request.
        """
        with _validated():
            method = GetConversions(
                from_date=from_date,
                to_date=to_date,
                page=page,
                size=size,
            )
        return await self(method)

    async def create_payment_link(
        self,
        *,
        payment_details: PaymentDetails,
        description: str | None = None,
        return_url: str | None = None,
        failed_url: str | None = None,
        payload: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentLinkResponse:
        """Create a payment link and let the payer choose the method.

        Unlike :meth:`create_transaction`, no payment method is fixed up
        front — the payer picks one on the hosted page.

        Returns:
            The hosted payment URL, transaction id, status and rate.
        """
        with _validated():
            method = CreatePaymentLink(
                payment_details=payment_details,
                description=description,
                return_url=return_url,
                failed_url=failed_url,
                payload=payload,
                metadata=metadata,
            )
        return await self(method)

    async def get_h2h_qr(self, transaction_id: str | UUID) -> H2HQrResponse:
        """Get the QR code or payment link for a host-to-host transaction."""
        with _validated():
            method = GetH2HQr(transaction_id=transaction_id)
        return await self(method)

    async def get_balances(self) -> BalancesResponse:
        """Get merchant balances, one entry per currency.

        The result is iterable::

            for balance in await client.get_balances():
                print(balance.currency, balance.amount)
        """
        return await self(GetBalances())

    async def check_cancel_supported(
        self,
        transaction_id: str | UUID,
    ) -> CancelSupportedResponse:
        """Check whether a transaction can be cancelled, and what it costs.

        A ``supported`` of ``False`` is a normal answer, not an error — read
        ``block_reason`` for why.
        """
        with _validated():
            method = CheckCancelSupported(transaction_id=transaction_id)
        return await self(method)

    async def cancel_transaction(
        self,
        transaction_id: str | UUID,
    ) -> CancelTransactionResponse:
        """Cancel a transaction and refund the payer.

        Call :meth:`check_cancel_supported` first: an ``accepted=False`` with
        ``manual_control_required=True`` means a human has to pick it up.
        """
        with _validated():
            method = CancelTransaction(transaction_id=transaction_id)
        return await self(method)

    async def export_transactions_csv(
        self,
        *,
        statuses: list[str] | None = None,
        payment_methods: list[str] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        time_zone_id: str | None = None,
    ) -> ExportUrlResponse:
        """Export filtered transactions to CSV, returning a download link."""
        with _validated():
            method = ExportTransactionsCsv(
                statuses=statuses,
                payment_methods=payment_methods,
                from_date=from_date,
                to_date=to_date,
                time_zone_id=time_zone_id,
            )
        return await self(method)

    async def export_transactions_excel(
        self,
        *,
        statuses: list[str] | None = None,
        payment_methods: list[str] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        time_zone_id: str | None = None,
    ) -> ExportUrlResponse:
        """Export filtered transactions to Excel, returning a download link."""
        with _validated():
            method = ExportTransactionsExcel(
                statuses=statuses,
                payment_methods=payment_methods,
                from_date=from_date,
                to_date=to_date,
                time_zone_id=time_zone_id,
            )
        return await self(method)

    async def export_transactions_json(
        self,
        *,
        statuses: list[str] | None = None,
        payment_methods: list[str] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        time_zone_id: str | None = None,
    ) -> TransactionExportResponse:
        """Export filtered transactions as JSON rows.

        Unlike the CSV and Excel exports, this returns the rows inline rather
        than a download link.
        """
        with _validated():
            method = ExportTransactionsJson(
                statuses=statuses,
                payment_methods=payment_methods,
                from_date=from_date,
                to_date=to_date,
                time_zone_id=time_zone_id,
            )
        return await self(method)

    async def create_subscription(
        self,
        *,
        payment_details: PaymentDetails,
        description: str | None = None,
    ) -> CreateSubscriptionResponse:
        """Create a recurring SBP subscription.

        Send the payer to the ``redirect`` URL to confirm the mandate. The
        ``transaction_id`` in the response is the subscription id — keep it,
        every later subscription call takes it.
        """
        with _validated():
            method = CreateSubscription(
                payment_details=payment_details,
                description=description,
            )
        return await self(method)

    async def get_subscription(self, subscription_id: str | UUID) -> Subscription:
        """Get a single subscription by id."""
        with _validated():
            method = GetSubscription(subscription_id=subscription_id)
        return await self(method)

    async def list_subscriptions(
        self,
        *,
        status: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> SubscriptionListResponse:
        """List subscriptions, optionally filtered by status and date range."""
        with _validated():
            method = ListSubscriptions(
                status=status,
                from_date=from_date,
                to_date=to_date,
                page=page,
                size=size,
            )
        return await self(method)

    async def cancel_subscription(
        self,
        subscription_id: str | UUID,
    ) -> CancelSubscriptionResponse:
        """Cancel a subscription, stopping all future charges.

        Idempotent. The payer can also cancel from the link in the emails sent
        after each charge, which arrives as a ``SUBSCRIPTION_CANCELLED``
        callback.
        """
        with _validated():
            method = CancelSubscription(subscription_id=subscription_id)
        return await self(method)

    async def close(self) -> None:
        """Close the underlying HTTP session and release resources."""
        if self._session is not None and self._owns_session:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> Platega:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
