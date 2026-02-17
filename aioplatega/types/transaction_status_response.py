from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import Field

from ..enums import PaymentStatus
from .base import PlategaObject
from .payment_details import PaymentDetails


class TransactionStatusResponse(PlategaObject):
    id: Optional[UUID] = None
    status: Optional[PaymentStatus] = None
    payment_details: Optional[PaymentDetails] = Field(None, alias="paymentDetails")
    merchant_name: Optional[str] = Field(None, alias="merchantName")
    merchant_id: Optional[UUID] = Field(None, alias="merchantId")
    commission: Optional[float] = Field(None, alias="comission")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    expires_in: Optional[str] = Field(None, alias="expiresIn")
    return_url: Optional[str] = Field(None, alias="return")
    commission_usdt: Optional[float] = Field(None, alias="comissionUsdt")
    amount_usdt: Optional[float] = Field(None, alias="amountUsdt")
    qr: Optional[str] = None
    pay_form_success_url: Optional[str] = Field(None, alias="payformSuccessUrl")
    payload: Optional[str] = None
    commission_type: Optional[int] = Field(None, alias="comissionType")
    external_id: Optional[str] = Field(None, alias="externalId")
    description: Optional[str] = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            id: Optional[UUID] = None,
            status: Optional[PaymentStatus] = None,
            payment_details: Optional[PaymentDetails] = None,
            merchant_name: Optional[str] = None,
            merchant_id: Optional[UUID] = None,
            commission: Optional[float] = None,
            payment_method: Optional[str] = None,
            expires_in: Optional[str] = None,
            return_url: Optional[str] = None,
            commission_usdt: Optional[float] = None,
            amount_usdt: Optional[float] = None,
            qr: Optional[str] = None,
            pay_form_success_url: Optional[str] = None,
            payload: Optional[str] = None,
            commission_type: Optional[int] = None,
            external_id: Optional[str] = None,
            description: Optional[str] = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                id=id,
                status=status,
                payment_details=payment_details,
                merchant_name=merchant_name,
                merchant_id=merchant_id,
                commission=commission,
                payment_method=payment_method,
                expires_in=expires_in,
                return_url=return_url,
                commission_usdt=commission_usdt,
                amount_usdt=amount_usdt,
                qr=qr,
                pay_form_success_url=pay_form_success_url,
                payload=payload,
                commission_type=commission_type,
                external_id=external_id,
                description=description,
                **__pydantic_kwargs,
            )
