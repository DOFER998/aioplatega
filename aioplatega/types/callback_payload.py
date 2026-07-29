from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import Field

from .base import PlategaObject


class CallbackPayload(PlategaObject):
    """Body of the transaction-status callback.

    Delivered to the callback URL configured in the dashboard, with the
    ``X-MerchantId`` and ``X-Secret`` headers for verification. Platega
    expects a response within 60 seconds and retries up to three times at
    five-minute intervals.

    Note:
        ``status`` is typed as a plain string rather than
        :class:`~aioplatega.enums.PaymentStatus`. The published schema lists
        only ``CONFIRMED`` and ``CANCELED``, while the same page's prose adds
        ``CHARGEBACKED`` for refunds, so the field has to admit values the
        schema does not name.
    """

    id: UUID
    amount: float
    currency: str
    status: str
    payment_method: int = Field(alias="paymentMethod")
    payload: str | None = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            id: UUID,
            amount: float,
            currency: str,
            status: str,
            payment_method: int,
            payload: str | None = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                id=id,
                amount=amount,
                currency=currency,
                status=status,
                payment_method=payment_method,
                payload=payload,
                **__pydantic_kwargs,
            )
