from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field

from aioplatega.types import RateResponse

from .base import PlategaMethod


class GetRate(PlategaMethod[RateResponse]):
    __api_method__: ClassVar[str] = "/rates/payment_method_rate"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = RateResponse

    merchant_id: str = Field(alias="merchantId")
    payment_method: int = Field(alias="paymentMethod")
    currency_from: str = Field(alias="currencyFrom")
    currency_to: str = Field(alias="currencyTo")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            merchant_id: str,
            payment_method: int,
            currency_from: str,
            currency_to: str,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                merchant_id=merchant_id,
                payment_method=payment_method,
                currency_from=currency_from,
                currency_to=currency_to,
                **__pydantic_kwargs,
            )
