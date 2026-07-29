from typing import ClassVar
from uuid import UUID

from pydantic import Field

from aioplatega.types import CancelTransactionResponse

from .base import PlategaMethod


class CancelTransaction(PlategaMethod[CancelTransactionResponse]):
    """POST ``/transaction/{id}/cancel`` — refund the payer."""

    __api_method__: ClassVar[str] = "/transaction/{transaction_id}/cancel"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = CancelTransactionResponse

    transaction_id: UUID = Field(alias="transactionId")
