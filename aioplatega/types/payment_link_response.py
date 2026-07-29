from pydantic import Field

from .base import PlategaObject


class PaymentLinkResponse(PlategaObject):
    """Response of ``POST v2/transaction/process`` (payer picks the method)."""

    transaction_id: str = Field(alias="transactionId")
    status: str
    url: str
    expires_in: str | None = Field(None, alias="expiresIn")
    rate: float | None = None
