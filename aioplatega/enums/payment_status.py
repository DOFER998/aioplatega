from enum import StrEnum


class PaymentStatus(StrEnum):
    """Transaction payment status values returned by the Platega API."""

    PENDING = "PENDING"
    CANCELED = "CANCELED"
    CONFIRMED = "CONFIRMED"
    CHARGEBACKED = "CHARGEBACKED"
