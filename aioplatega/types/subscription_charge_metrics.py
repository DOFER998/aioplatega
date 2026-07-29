from pydantic import Field

from .base import PlategaObject


class SubscriptionChargeMetrics(PlategaObject):
    """Charge history of a subscription, as reported alongside it."""

    charges_total: int | None = Field(None, alias="chargesTotal")
    charges_success: int | None = Field(None, alias="chargesSuccess")
    charges_failed: int | None = Field(None, alias="chargesFailed")
    total_amount: float | None = Field(None, alias="totalAmount")
    last_charge_at: str | None = Field(None, alias="lastChargeAt")
    next_charge_at: str | None = Field(None, alias="nextChargeAt")
