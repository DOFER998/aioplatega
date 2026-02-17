from typing import TYPE_CHECKING, Any

from .base import PlategaObject


class PaymentDetails(PlategaObject):
    amount: float
    currency: str

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            amount: float,
            currency: str,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                amount=amount,
                currency=currency,
                **__pydantic_kwargs,
            )
