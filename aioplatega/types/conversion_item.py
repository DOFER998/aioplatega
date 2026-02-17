from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from pydantic import Field

from .base import PlategaObject


class ConversionItem(PlategaObject):
    id: Optional[int] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            id: Optional[int] = None,
            amount: Optional[float] = None,
            currency: Optional[str] = None,
            status: Optional[str] = None,
            created_at: Optional[datetime] = None,
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
