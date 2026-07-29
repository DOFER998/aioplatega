from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import AliasChoices, Field

from ..enums import PaymentStatus
from .base import PlategaObject
from .payment_details import PaymentDetails


class TransactionStatusResponse(PlategaObject):
    """Full state of a transaction.

    Note:
        ``merchant_id`` accepts both ``mechantId`` and ``merchantId``. The API
        spells it ``mechantId`` in the published schema and in its own example;
        the correct spelling is accepted as well, should the typo ever be
        fixed server-side.

        Several other fields keep the API's spelling in their aliases for the
        same reason: ``comission``, ``comissionUsdt``, ``comissionType``.
    """

    id: UUID | None = None
    status: PaymentStatus | str | None = None
    payment_details: PaymentDetails | None = Field(None, alias="paymentDetails")
    merchant_name: str | None = Field(None, alias="merchantName")
    merchant_id: UUID | None = Field(
        None, validation_alias=AliasChoices("mechantId", "merchantId"), alias="mechantId"
    )
    commission: float | None = Field(None, alias="comission")
    payment_method: str | None = Field(None, alias="paymentMethod")
    expires_in: str | None = Field(None, alias="expiresIn")
    return_url: str | None = Field(None, alias="return")
    commission_usdt: float | None = Field(None, alias="comissionUsdt")
    amount_usdt: float | None = Field(None, alias="amountUsdt")
    qr: str | None = None
    pay_form_success_url: str | None = Field(None, alias="payformSuccessUrl")
    payload: str | None = None
    commission_type: int | None = Field(None, alias="comissionType")
    external_id: str | None = Field(None, alias="externalId")
    description: str | None = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            id: UUID | None = None,
            status: PaymentStatus | str | None = None,
            payment_details: PaymentDetails | None = None,
            merchant_name: str | None = None,
            merchant_id: UUID | None = None,
            commission: float | None = None,
            payment_method: str | None = None,
            expires_in: str | None = None,
            return_url: str | None = None,
            commission_usdt: float | None = None,
            amount_usdt: float | None = None,
            qr: str | None = None,
            pay_form_success_url: str | None = None,
            payload: str | None = None,
            commission_type: int | None = None,
            external_id: str | None = None,
            description: str | None = None,
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
