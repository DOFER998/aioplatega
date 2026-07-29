from pydantic import Field

from .base import PlategaObject


class SubscriptionChargeCallback(PlategaObject):
    """Callback delivered on every subscription charge, successful or not.

    Field names arrive PascalCase here, unlike the camelCase used by the
    plain transaction callback.
    """

    id: str = Field(alias="Id")
    amount: float = Field(alias="Amount")
    currency: str = Field(alias="Currency")
    status: str = Field(alias="Status")
    payment_method: int | None = Field(None, alias="PaymentMethod")
    payload: str | None = Field(None, alias="Payload")
    subscription_id: str | None = Field(None, alias="SubscriptionId")
    next_charge_at: str | None = Field(None, alias="NextChargeAt")


class SubscriptionStatusCallback(PlategaObject):
    """Callback delivered when a subscription changes state.

    Here ``id`` is the subscription id, not a transaction id.
    """

    id: str = Field(alias="Id")
    amount: float | None = Field(None, alias="Amount")
    currency: str | None = Field(None, alias="Currency")
    status: str = Field(alias="Status")
    payment_method: int | None = Field(None, alias="PaymentMethod")
    payload: str | None = Field(None, alias="Payload")
    subscription_id: str | None = Field(None, alias="SubscriptionId")
    next_charge_at: str | None = Field(None, alias="NextChargeAt")
