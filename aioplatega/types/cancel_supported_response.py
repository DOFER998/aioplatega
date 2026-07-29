from pydantic import Field

from .base import PlategaObject


class CancelSupportedResponse(PlategaObject):
    """Whether a transaction can be cancelled, and what it would cost.

    A ``supported`` of ``False`` is a normal answer, not an error: read
    :attr:`block_reason` for why.
    """

    supported: bool
    total_deduct_usdt: float | None = Field(None, alias="totalDeductUsdt")
    penalty_native_amount: float | None = Field(None, alias="penaltyNativeAmount")
    penalty_native_currency: str | None = Field(None, alias="penaltyNativeCurrency")
    penalty_usdt: float | None = Field(None, alias="penaltyUsdt")
    penalty_conversion_rate: float | None = Field(None, alias="penaltyConversionRate")
    block_reason: str | None = Field(None, alias="blockReason")
