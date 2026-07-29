from pydantic import Field, RootModel

from .base import PlategaObject, SequenceResponse


class TransactionExportItem(PlategaObject):
    """One transaction row from the JSON export."""

    record_id: str | None = Field(None, alias="recordId")
    created_at: str | None = Field(None, alias="createdAt")
    amount: float | None = None
    currency_code: str | None = Field(None, alias="currencyCode")
    status: str | None = None
    payment_method: str | None = Field(None, alias="paymentMethod")
    description: str | None = None
    payload: str | None = None


class TransactionExportResponse(SequenceResponse, RootModel[list[TransactionExportItem]]):
    """The JSON export: a bare array of transaction rows."""
