from enum import StrEnum


class PaymentStatus(StrEnum):
    """Transaction payment status.

    Note:
        Platega publishes its statuses in three places that disagree. The
        Apidog schema at https://docs.platega.io lists ``PENDING``,
        ``CANCELED``, ``CONFIRMED`` and ``CHARGEBACKED``; the older GitBook
        adds ``EXPIRED`` and ``FAILED``; the callback schema adds ``DISPUTED``
        and ``PARTIALLY_REFUNDED``.

        Response models type their status field as ``PaymentStatus | str``, so
        a value absent from these lists still parses rather than making the
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

    DISPUTED = "DISPUTED"
    """Under review: the funds are reserved until the dispute is resolved.

    Resolves to :attr:`CONFIRMED`, if the merchant wins, or
    :attr:`CHARGEBACKED`, if the payer is refunded. The amount is frozen in
    ``disputeFrozenBalance`` on the USDT balance while the review lasts.
    """

    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    """Part of the payment was refunded; the rest stays credited.

    Documented only for the callback, and sent again on every further partial
    refund of the same payment.
    """

    EXPIRED = "EXPIRED"
    """The payment window closed before the payer completed it."""

    FAILED = "FAILED"
    """The payment could not be created."""
