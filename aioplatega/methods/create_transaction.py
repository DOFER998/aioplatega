from typing import TYPE_CHECKING, Any, ClassVar, Optional

from pydantic import Field

from aioplatega.enums import PaymentMethodInt
from aioplatega.types import CreateTransactionResponse, PaymentDetails

from .base import PlategaMethod


class CreateTransaction(PlategaMethod[CreateTransactionResponse]):
    __api_method__: ClassVar[str] = "/transaction/process"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = CreateTransactionResponse

    payment_method: PaymentMethodInt = Field(alias="paymentMethod")
    payment_details: PaymentDetails = Field(alias="paymentDetails")
    description: Optional[str] = None
    return_url: Optional[str] = Field(None, alias="return")
    failed_url: Optional[str] = Field(None, alias="failedUrl")
    payload: Optional[str] = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: PaymentMethodInt,
            payment_details: PaymentDetails,
            description: Optional[str] = None,
            return_url: Optional[str] = None,
            failed_url: Optional[str] = None,
            payload: Optional[str] = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                payment_method=payment_method,
                payment_details=payment_details,
                description=description,
                return_url=return_url,
                failed_url=failed_url,
                payload=payload,
                **__pydantic_kwargs,
            )
