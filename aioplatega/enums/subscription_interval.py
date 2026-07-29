from enum import StrEnum


class SubscriptionInterval(StrEnum):
    """How often a subscription charges.

    Required when creating a subscription, as ``paymentDetails.interval``.
    """

    DAY = "1"
    """Charged daily."""

    WEEK = "2"
    """Charged weekly."""

    MONTH = "3"
    """Charged monthly."""

    YEAR = "4"
    """Charged yearly."""
