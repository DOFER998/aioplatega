from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID

from pydantic import Field

from aioplatega.types import TransactionStatusResponse

from .base import PlategaMethod


class GetTransactionStatus(PlategaMethod[TransactionStatusResponse]):
    __api_method__: ClassVar[str] = "/transaction/{transaction_id}"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = TransactionStatusResponse

    transaction_id: UUID = Field(alias="transactionId")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            transaction_id: UUID,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                transaction_id=transaction_id,
                **__pydantic_kwargs,
            )
