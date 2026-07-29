from pydantic import Field

from .base import PlategaObject


class CreateSubscriptionResponse(PlategaObject):
    """Response to creating a subscription.

    ``transaction_id`` is the *subscription* id — keep it, it is what every
    later subscription call takes.
    """

    payment_method: str | None = Field(None, alias="paymentMethod")
    transaction_id: str | None = Field(None, alias="transactionId")
    redirect: str | None = None
    status: str | None = None
    merchant_id: str | None = Field(None, alias="merchantId")
