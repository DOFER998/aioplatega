from datetime import datetime

from pydantic import Field

from .base import PlategaObject


class RateResponse(PlategaObject):
    """An exchange rate between two currencies for a payment method.

    Note:
        ``updated_at`` appears in the GitBook example but not in live
        responses, so it is optional. Rates are directional: a pair the API
        answers in one direction may return 404 in the other.
    """

    id: str | None = None
    merchant_id: str | None = Field(None, alias="merchantId")
    payment_method: int | None = Field(None, alias="paymentMethod")
    currency_from: str | None = Field(None, alias="currencyFrom")
    currency_to: str | None = Field(None, alias="currencyTo")
    rate: float | None = None
    updated_at: datetime | None = Field(None, alias="updatedAt")
