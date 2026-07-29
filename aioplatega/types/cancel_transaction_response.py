from pydantic import Field

from .base import PlategaObject


class CancelTransactionResponse(PlategaObject):
    """Outcome of a cancellation request.

    ``accepted=False`` with ``manual_control_required=True`` means the refund
    could not be automated and a human has to pick it up.
    """

    transaction_id: str | None = Field(None, alias="transactionId")
    accepted: bool | None = None
    manual_control_required: bool | None = Field(None, alias="manualControlRequired")
    message: str | None = None
