from typing import ClassVar
from uuid import UUID

from pydantic import Field

from aioplatega.types import CancelSupportedResponse

from .base import PlategaMethod


class CheckCancelSupported(PlategaMethod[CancelSupportedResponse]):
    """GET ``/transaction/{id}/cancel-supported``.

    Worth calling before :class:`~aioplatega.methods.CancelTransaction`: it
    reports both whether cancellation is possible and what it will cost.
    """

    __api_method__: ClassVar[str] = "/transaction/{transaction_id}/cancel-supported"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = CancelSupportedResponse

    transaction_id: UUID = Field(alias="transactionId")
