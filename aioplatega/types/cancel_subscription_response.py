from pydantic import Field

from .base import PlategaObject


class CancelSubscriptionResponse(PlategaObject):
    """Result of cancelling a subscription. The endpoint is idempotent."""

    subscription_id: str | None = Field(None, alias="subscriptionId")
    status: str | None = None
