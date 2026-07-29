from pydantic import Field, RootModel

from .base import PlategaObject, SequenceResponse


class BalanceItem(PlategaObject):
    """Merchant balance in a single currency."""

    amount: float | None = None
    currency: str | None = None
    frozen_balance: float | None = Field(None, alias="frozenBalance")


class BalancesResponse(SequenceResponse, RootModel[list[BalanceItem]]):
    """``GET /balance/all``: a bare array of per-currency balances."""
