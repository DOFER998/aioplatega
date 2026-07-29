from enum import StrEnum


class SubscriptionInterval(StrEnum):
    """Subscription billing interval, as reported on a subscription.

    Read-only in practice: the create-subscription body carries only
    ``paymentMethod``, ``paymentDetails`` and ``description``, so the period
    is configured in the dashboard rather than sent through the API.

    Warning:
        The published schema lists the raw values ``"1"``-``"4"`` and never
        says what they mean, while the API's own examples return
        ``intervalUnit`` as both a number (``2``, ``3``) and a word
        (``"Month"``). Members are therefore named after the values rather
        than after a guessed period: naming ``"3"`` ``MONTH`` on the strength
        of one example would risk misreporting the billing cycle.
    """

    INTERVAL_1 = "1"
    INTERVAL_2 = "2"
    INTERVAL_3 = "3"
    INTERVAL_4 = "4"
