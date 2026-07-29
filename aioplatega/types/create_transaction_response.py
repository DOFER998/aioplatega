from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import Field

from ..enums import PaymentStatus
from .base import PlategaObject
from .payment_details import PaymentDetails


class CreateTransactionResponse(PlategaObject):
    """A created transaction, including the URL to send the payer to."""

    payment_method: str | None = Field(None, alias="paymentMethod")
    transaction_id: UUID = Field(alias="transactionId")
    redirect: str | None = None
    return_url: str | None = Field(None, alias="return")
    payment_details: str | PaymentDetails | None = Field(None, alias="paymentDetails")
    status: PaymentStatus
    expires_in: str | None = Field(None, alias="expiresIn")
    merchant_id: UUID | None = Field(None, alias="merchantId")
    usdt_rate: float | None = Field(None, alias="usdtRate")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: str | None = None,
            transaction_id: UUID,
            redirect: str | None = None,
            return_url: str | None = None,
            payment_details: str | PaymentDetails | None = None,
            status: PaymentStatus,
            expires_in: str | None = None,
            merchant_id: UUID | None = None,
            usdt_rate: float | None = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                payment_method=payment_method,
                transaction_id=transaction_id,
                redirect=redirect,
                return_url=return_url,
                payment_details=payment_details,
                status=status,
                expires_in=expires_in,
                merchant_id=merchant_id,
                usdt_rate=usdt_rate,
                **__pydantic_kwargs,
            )
