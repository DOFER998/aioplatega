from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import Field

from .base import PlategaObject


class ConversionItem(PlategaObject):
    id: int | None = None
    amount: float | None = None
    currency: str | None = None
    status: str | None = None
    created_at: datetime | None = Field(None, alias="createdAt")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            id: int | None = None,
            amount: float | None = None,
            currency: str | None = None,
            status: str | None = None,
            created_at: datetime | None = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                id=id,
                amount=amount,
                currency=currency,
                status=status,
                created_at=created_at,
                **__pydantic_kwargs,
            )
