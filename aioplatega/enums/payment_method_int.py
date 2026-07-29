from enum import IntEnum


class PaymentMethodInt(IntEnum):
    """Supported payment method identifiers.

    Note:
        Drawn from both published specifications. The Apidog schema at
        https://docs.platega.io lists 2, 3, 11, 12 and 13; the older GitBook
        additionally names 10. Its table also notes that methods 1 through 9
        are P2P, which is why the subscription endpoint takes a method id
        that is not a member here.
    """

    SBP_QR = 2
    """SBP QR code, plus SberPay where the merchant has it enabled."""

    ERIP = 3
    """ERIP (Belarusian payment system)."""

    CARDS_RUB = 10
    """Card payments in RUB, 3-D Secure, MIR cards.

    Named in the GitBook table but absent from the Apidog enum.
    """

    CARD_ACQUIRING = 11
    """Card acquiring."""

    INTERNATIONAL_ACQUIRING = 12
    """International payments."""

    CRYPTO = 13
    """Cryptocurrency."""
