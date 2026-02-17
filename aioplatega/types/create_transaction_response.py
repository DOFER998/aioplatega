from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import Field

from ..enums import PaymentStatus
from .base import PlategaObject
from .payment_details import PaymentDetails


class CreateTransactionResponse(PlategaObject):
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    transaction_id: UUID = Field(alias="transactionId")
    redirect: Optional[str] = None
    return_url: Optional[str] = Field(None, alias="return")
    payment_details: Optional[str | PaymentDetails] = Field(None, alias="paymentDetails")
    status: PaymentStatus
    expires_in: Optional[str] = Field(None, alias="expiresIn")
    merchant_id: Optional[UUID] = Field(None, alias="merchantId")
    usdt_rate: Optional[float] = Field(None, alias="usdtRate")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: Optional[str] = None,
            transaction_id: UUID,
            redirect: Optional[str] = None,
            return_url: Optional[str] = None,
            payment_details: Optional[str | PaymentDetails] = None,
            status: PaymentStatus,
            expires_in: Optional[str] = None,
            merchant_id: Optional[UUID] = None,
            usdt_rate: Optional[float] = None,
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
