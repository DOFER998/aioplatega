from enum import Enum


class PaymentStatus(str, Enum):
    """Transaction payment status values returned by the Platega API."""

    PENDING = "PENDING"
    CANCELED = "CANCELED"
    CONFIRMED = "CONFIRMED"
    CHARGEBACKED = "CHARGEBACKED"
