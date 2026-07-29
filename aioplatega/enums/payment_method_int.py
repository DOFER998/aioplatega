from enum import IntEnum


class PaymentMethodInt(IntEnum):
    """Supported payment method identifiers.

    Values follow the ``PaymentMethodInt`` schema published at
    https://docs.platega.io — with the exception of :attr:`CARDS_RUB`.
    """

    SBP_QR = 2
    """SBP QR code, plus SberPay where the merchant has it enabled."""

    ERIP = 3
    """ERIP (Belarusian payment system)."""

    CARDS_RUB = 10
    """Deprecated: absent from the published API documentation.

    Kept so that existing callers keep importing, but the API is not
    documented as accepting ``10``. Prefer :attr:`CARD_ACQUIRING`.
    """

    CARD_ACQUIRING = 11
    """Card acquiring."""

    INTERNATIONAL_ACQUIRING = 12
    """International payments."""

    CRYPTO = 13
    """Cryptocurrency."""
