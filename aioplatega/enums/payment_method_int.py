from enum import Enum


class PaymentMethodInt(int, Enum):
    """Supported payment method identifiers."""

    SBP_QR = 2
    CARDS_RUB = 10
    CARD_ACQUIRING = 11
    INTERNATIONAL_ACQUIRING = 12
    CRYPTO = 13
