from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import Field

from .base import PlategaObject


class RateResponse(PlategaObject):
    payment_method: int | None = Field(None, alias="paymentMethod")
    currency_from: str | None = Field(None, alias="currencyFrom")
    currency_to: str | None = Field(None, alias="currencyTo")
    rate: float | None = None
    updated_at: datetime | None = Field(None, alias="updatedAt")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: int | None = None,
            currency_from: str | None = None,
            currency_to: str | None = None,
            rate: float | None = None,
            updated_at: datetime | None = None,
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
