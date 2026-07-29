from pydantic import Field

from ..enums import SubscriptionInterval
from .base import PlategaObject


class SubscriptionPaymentDetails(PlategaObject):
    """Amount, currency and charge period of a subscription.

    Distinct from :class:`~aioplatega.types.PaymentDetails`: a subscription
    charges repeatedly, so the period is part of the payment details and is
    required.

    Note:
        ``amount`` is an integer here. The subscription create schema types it
        that way, unlike the one-off payment schema, which takes a number.
    """

    amount: int
    currency: str
    interval: SubscriptionInterval = Field(
        description="Charge period: 1 day, 2 week, 3 month, 4 year.",
    )
