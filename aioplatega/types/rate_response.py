from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from pydantic import Field

from .base import PlategaObject


class RateResponse(PlategaObject):
    payment_method: Optional[int] = Field(None, alias="paymentMethod")
    currency_from: Optional[str] = Field(None, alias="currencyFrom")
    currency_to: Optional[str] = Field(None, alias="currencyTo")
    rate: Optional[float] = None
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: Optional[int] = None,
            currency_from: Optional[str] = None,
            currency_to: Optional[str] = None,
            rate: Optional[float] = None,
            updated_at: Optional[datetime] = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                payment_method=payment_method,
                currency_from=currency_from,
                currency_to=currency_to,
                rate=rate,
                updated_at=updated_at,
                **__pydantic_kwargs,
            )
