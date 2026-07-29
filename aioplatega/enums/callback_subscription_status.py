from enum import StrEnum


class CallbackSubscriptionStatus(StrEnum):
    """Subscription status as delivered in a subscription callback.

    Distinct from :class:`~aioplatega.enums.SubscriptionStatus`: the callback
    reports transitions in SCREAMING_SNAKE form, the resource reports state in
    PascalCase.
    """

    ACTIVATED = "SUBSCRIPTION_ACTIVATED"
    PAST_DUE = "SUBSCRIPTION_PAST_DUE"
    CANCELLED = "SUBSCRIPTION_CANCELLED"
    FAILED = "SUBSCRIPTION_FAILED"
