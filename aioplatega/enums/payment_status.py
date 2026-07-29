from enum import StrEnum


class PaymentStatus(StrEnum):
    """Transaction payment status.

    Note:
        Platega publishes two specifications that disagree. The Apidog schema
        at https://docs.platega.io lists ``PENDING``, ``CANCELED``,
        ``CONFIRMED`` and ``CHARGEBACKED``; the older GitBook lists
        ``PENDING``, ``CONFIRMED``, ``EXPIRED``, ``CANCELED`` and ``FAILED``.
        Both sets are accepted here, since the API answers with values from
        each.

        Response models type their status field as ``PaymentStatus | str``, so
        a value absent from both lists still parses rather than making the
        whole response unreadable.
    """

    PENDING = "PENDING"
    """Awaiting payment."""

    CONFIRMED = "CONFIRMED"
    """Paid."""

    CANCELED = "CANCELED"
    """Payment failed or was cancelled."""

    CHARGEBACKED = "CHARGEBACKED"
    """Funds were charged back."""

    EXPIRED = "EXPIRED"
    """The payment window closed before the payer completed it."""

    FAILED = "FAILED"
    """The payment could not be created."""
