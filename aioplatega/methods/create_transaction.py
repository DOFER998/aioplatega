from typing import ClassVar

from aioplatega.types import CreateTransactionRequest, CreateTransactionResponse

from .base import PlategaMethod


class CreateTransaction(CreateTransactionRequest, PlategaMethod[CreateTransactionResponse]):
    """POST ``/transaction/process``.

    The request body is defined once, by
    :class:`~aioplatega.types.CreateTransactionRequest`; this class only binds
    it to an endpoint. Field declarations (and the ``__init__`` stub that gives
    type checkers a signature) are inherited, so the two cannot drift apart.
    """

    __api_method__: ClassVar[str] = "/transaction/process"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = CreateTransactionResponse
