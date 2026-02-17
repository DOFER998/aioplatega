from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import Field

from .base import PlategaObject


class CallbackPayload(PlategaObject):
    id: UUID
    amount: float
    currency: str
    status: str
    payment_method: int = Field(alias="paymentMethod")
    payload: Optional[str] = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            id: UUID,
            amount: float,
            currency: str,
            status: str,
            payment_method: int,
            payload: Optional[str] = None,
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
