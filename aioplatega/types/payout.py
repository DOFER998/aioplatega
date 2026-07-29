from pydantic import Field

from .base import PlategaObject


class CardPayoutRequest(PlategaObject):
    """Body of ``POST /api/v1/payouts/card-rub``.

    Supply either :attr:`card_id` or :attr:`card_number`, not both.
    """

    card_id: str | None = Field(None, alias="cardId")
    card_number: str | None = Field(None, alias="cardNumber")
    amount_rub: int = Field(alias="amountRub")
    payout_method: str = Field("CARD", alias="payoutMethod")
    currency_requested: str = Field("RUB", alias="currencyRequested")


class CardPayoutResponse(PlategaObject):
    """A created payout. Status is ``CREATED`` immediately after creation."""

    withdrawal_record_id: str | None = Field(None, alias="withdrawalRecordId")
    status: str | None = None
    card_masked: str | None = Field(None, alias="cardMasked")
    amount_usdt_debited: float | None = Field(None, alias="amountUsdtDebited")
