from pydantic import Field

from .base import PlategaObject
from .subscription_charge_metrics import SubscriptionChargeMetrics


class Subscription(PlategaObject):
    """A recurring SBP subscription.

    ``status`` and ``interval_unit`` are deliberately loose. The vendor's own
    examples return each of them as a number in the list response and as a
    word in the single-subscription response (``status: 4`` versus
    ``status: "Active"``), so pinning either to one type would reject half the
    real payloads. See :class:`~aioplatega.enums.SubscriptionStatus` and
    :class:`~aioplatega.enums.SubscriptionInterval`.
    """

    id: str | None = None
    status: str | int | None = None
    amount: float | None = None
    currency_code: str | None = Field(None, alias="currencyCode")
    interval_unit: str | int | None = Field(None, alias="intervalUnit")
    interval_count: int | None = Field(None, alias="intervalCount")
    start_at: str | None = Field(None, alias="startAt")
    next_charge_at: str | None = Field(None, alias="nextChargeAt")
    last_charge_at: str | None = Field(None, alias="lastChargeAt")
    description: str | None = None
    created_at: str | None = Field(None, alias="createdAt")
    customer_email: str | None = Field(None, alias="customerEmail")
    charge_metrics: SubscriptionChargeMetrics | None = Field(None, alias="chargeMetrics")
