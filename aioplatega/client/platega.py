from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import ValidationError

from aioplatega.callback import verify_callback
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
    CallbackPayload,
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
    SubscriptionPaymentDetails,
    TransactionExportResponse,
    TransactionStatusResponse,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
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

    Example:
        .. code-block:: python

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
        payment_method: PaymentMethodInt | int,
        payment_details: PaymentDetails,
        description: str | None = None,
        return_url: str | None = None,
        failed_url: str | None = None,
        payload: str | None = None,
    ) -> CreateTransactionResponse:
        """Create a new payment transaction.

        Args:
            payment_method: Payment method identifier, e.g.
                ``PaymentMethodInt.SBP_QR``. Any integer the merchant is
                enabled for is accepted, including ids the enum does not name.
            payment_details: Amount and currency for the payment.
            description: Optional human-readable description.
            return_url: URL to redirect the user after successful payment.
            failed_url: URL to redirect the user after failed payment.
            payload: Arbitrary string passed through to the callback.
            metadata: Extra data required for some merchant categories.

        Returns:
            Response containing the transaction ID, status, and redirect URL.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.

        Note:
        ``metadata`` carries the payer identifier. Shops in certain categories
        are required to send ``metadata.userId``; where that requirement
        applies, omitting it disables antifraud protection and can get the
        shop suspended. Ask your Platega manager whether it applies to yours.
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

        Note:
            Documented in the older GitBook rather than at
            https://docs.platega.io, which does not list this endpoint at all.
            It is live, but treat the omission as a sign that it may be
            withdrawn without notice.
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
        front: the payer picks one on the hosted page.

        Args:
            payment_details: Amount and currency for the payment.
            description: Human-readable description shown to the payer.
            return_url: Where to send the payer after a successful payment.
            failed_url: Where to send the payer after a failed payment.
            payload: Arbitrary string passed through to the callback.
            metadata: Extra data required for some merchant categories.

        Returns:
            The hosted payment URL, transaction id, status and rate.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.

        Note:
        ``metadata`` carries the payer identifier. Shops in certain categories
        are required to send ``metadata.userId``; where that requirement
        applies, omitting it disables antifraud protection and can get the
        shop suspended. Ask your Platega manager whether it applies to yours.
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
        """Get the QR code or payment link for a host-to-host transaction.

        Args:
            transaction_id: UUID of the transaction, as a :class:`~uuid.UUID`
                or its string form.

        Returns:
            The amount and the QR payload or link.

        Raises:
            PlategaValidationError: If ``transaction_id`` is not a valid UUID.
        """
        with _validated():
            method = GetH2HQr(transaction_id=transaction_id)
        return await self(method)

    async def get_balances(self) -> BalancesResponse:
        """Get merchant balances, one entry per currency.

        Returns:
            An iterable of :class:`~aioplatega.types.BalanceItem`.

        Example:
            .. code-block:: python

                for balance in await client.get_balances():
                    print(balance.currency, balance.amount)
        """
        return await self(GetBalances())

    async def check_cancel_supported(
        self,
        transaction_id: str | UUID,
    ) -> CancelSupportedResponse:
        """Check whether a transaction can be cancelled, and what it costs.

        Args:
            transaction_id: UUID of the transaction, as a :class:`~uuid.UUID`
                or its string form.

        Returns:
            Whether cancellation is possible and the USDT it would deduct. A
            ``supported`` of ``False`` is a normal answer, not an error; read
            ``block_reason`` for why.

        Raises:
            PlategaValidationError: If ``transaction_id`` is not a valid UUID.
        """
        with _validated():
            method = CheckCancelSupported(transaction_id=transaction_id)
        return await self(method)

    async def cancel_transaction(
        self,
        transaction_id: str | UUID,
    ) -> CancelTransactionResponse:
        """Cancel a transaction and refund the payer.

        Args:
            transaction_id: UUID of the transaction, as a :class:`~uuid.UUID`
                or its string form.

        Returns:
            The outcome. An ``accepted`` of ``False`` with
            ``manual_control_required`` set means a human has to pick it up.

        Raises:
            PlategaValidationError: If ``transaction_id`` is not a valid UUID.

        Note:
            Call :meth:`check_cancel_supported` first to learn whether the
            cancellation is possible and what it will cost.
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
        """Export filtered transactions to CSV.

        Args:
            statuses: Restrict to these transaction statuses.
            payment_methods: Restrict to these payment method names.
            from_date: Start of the period, as an ISO date string.
            to_date: End of the period, as an ISO date string.
            time_zone_id: Time zone the dates are expressed in, e.g.
                ``"Europe/Moscow"``.

        Returns:
            A link to the generated file.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.
        """
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
        """Export filtered transactions to Excel.

        Args:
            statuses: Restrict to these transaction statuses.
            payment_methods: Restrict to these payment method names.
            from_date: Start of the period, as an ISO date string.
            to_date: End of the period, as an ISO date string.
            time_zone_id: Time zone the dates are expressed in, e.g.
                ``"Europe/Moscow"``.

        Returns:
            A link to the generated file.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.
        """
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

        Args:
            statuses: Restrict to these transaction statuses.
            payment_methods: Restrict to these payment method names.
            from_date: Start of the period, as an ISO date string.
            to_date: End of the period, as an ISO date string.
            time_zone_id: Time zone the dates are expressed in, e.g.
                ``"Europe/Moscow"``.

        Returns:
            An iterable of :class:`~aioplatega.types.TransactionExportItem`.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.
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
        payment_details: SubscriptionPaymentDetails,
        description: str | None = None,
    ) -> CreateSubscriptionResponse:
        """Create a recurring SBP subscription.

        Args:
            payment_details: Amount, currency and charge period. The period is
                required — see
                :class:`~aioplatega.types.SubscriptionPaymentDetails`.
            description: Shown to the payer on the payment form and in the
                email sent after each charge.

        Returns:
            The subscription, including the ``redirect`` URL to send the payer
            to so they can confirm the mandate.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.

        Note:
            ``transaction_id`` in the response is the subscription id. Keep
            it: every later subscription call takes it.
        """
        with _validated():
            method = CreateSubscription(
                payment_details=payment_details,
                description=description,
            )
        return await self(method)

    async def get_subscription(self, subscription_id: str | UUID) -> Subscription:
        """Get a single subscription by id.

        Args:
            subscription_id: UUID of the subscription, as a
                :class:`~uuid.UUID` or its string form.

        Returns:
            The subscription and its charge schedule.

        Raises:
            PlategaValidationError: If ``subscription_id`` is not a valid UUID.
        """
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
        """List subscriptions, optionally filtered by status and date range.

        Args:
            status: Restrict to subscriptions in this state.
            from_date: Start of the period, as an ISO date string.
            to_date: End of the period, as an ISO date string.
            page: Zero-based page number.
            size: Number of items per page.

        Returns:
            One page of subscriptions, with the total count.

        Raises:
            PlategaValidationError: If the arguments are not a valid request.
        """
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

        Args:
            subscription_id: UUID of the subscription, as a
                :class:`~uuid.UUID` or its string form.

        Returns:
            The subscription id and its resulting status.

        Raises:
            PlategaValidationError: If ``subscription_id`` is not a valid UUID.

        Note:
            Idempotent. The payer can also cancel from the link in the emails
            sent after each charge, which arrives as a
            ``SUBSCRIPTION_CANCELLED`` callback.
        """
        with _validated():
            method = CancelSubscription(subscription_id=subscription_id)
        return await self(method)

    def verify_callback(
        self,
        headers: Mapping[str, str],
        body: str | bytes,
        *,
        model: type[Any] = CallbackPayload,
    ) -> Any:
        """Authenticate an incoming callback against this client's credentials.

        Platega authenticates callbacks by echoing your own ``X-MerchantId``
        and ``X-Secret`` back at you; the comparison is done in constant time.

        Args:
            headers: Request headers, looked up case-insensitively.
            body: Raw request body.
            model: Model to parse the body into. Pass
                :class:`~aioplatega.types.SubscriptionChargeCallback` or
                :class:`~aioplatega.types.SubscriptionStatusCallback` for the
                subscription callbacks.

        Returns:
            The parsed callback body, an instance of ``model``.

        Raises:
            PlategaValidationError: If the credentials do not match or the body
                cannot be parsed.
        """
        return verify_callback(
            headers,
            body,
            merchant_id=self._merchant_id,
            secret=self._secret,
            model=model,
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
