from typing import TYPE_CHECKING, Any

from pydantic import Field

from ..enums import PaymentMethodInt
from .base import PlategaObject
from .payment_details import PaymentDetails


class CreateTransactionRequest(PlategaObject):
    """Body for creating a transaction.

    Note:
        Do not supply an ``id``. The API generates the transaction id.
    """

    payment_method: PaymentMethodInt = Field(alias="paymentMethod")
    payment_details: PaymentDetails = Field(alias="paymentDetails")
    description: str | None = None
    return_url: str | None = Field(None, alias="return")
    failed_url: str | None = Field(None, alias="failedUrl")
    payload: str | None = None
    metadata: dict[str, Any] | None = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: PaymentMethodInt,
            payment_details: PaymentDetails,
            description: str | None = None,
            return_url: str | None = None,
            failed_url: str | None = None,
            payload: str | None = None,
            metadata: dict[str, Any] | None = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                payment_method=payment_method,
                payment_details=payment_details,
                description=description,
                return_url=return_url,
                failed_url=failed_url,
                payload=payload,
                metadata=metadata,
                **__pydantic_kwargs,
            )
