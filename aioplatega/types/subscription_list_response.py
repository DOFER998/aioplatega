from pydantic import Field

from .base import PlategaObject
from .subscription import Subscription


class SubscriptionListResponse(PlategaObject):
    """A page of subscriptions."""

    items: list[Subscription] = Field(default_factory=list)
    total: int = 0
    page: int = 0
    size: int = 0
