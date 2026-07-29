from enum import StrEnum


class SubscriptionStatus(StrEnum):
    """Lifecycle state of a recurring SBP subscription."""

    PENDING_AGREEMENT = "PendingAgreement"
    ACTIVE = "Active"
    PAST_DUE = "PastDue"
    CANCELLED = "Cancelled"
    FAILED = "Failed"
