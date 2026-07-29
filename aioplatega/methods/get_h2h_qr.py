from typing import ClassVar
from uuid import UUID

from pydantic import Field

from aioplatega.types import H2HQrResponse

from .base import PlategaMethod


class GetH2HQr(PlategaMethod[H2HQrResponse]):
    """GET ``/h2h/{id}`` — QR code or payment link for a host-to-host payment."""

    __api_method__: ClassVar[str] = "/h2h/{transaction_id}"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = H2HQrResponse

    transaction_id: UUID = Field(alias="transactionId")
