from pydantic import Field

from .base import PlategaObject


class ConversionItem(PlategaObject):
    """One balance-unlock operation: a conversion between two currencies.

    Note:
        Built from live responses. The published example for this endpoint is
        an empty object, so the specification describes none of these fields.
    """

    id: str | None = None
    merchant_id: str | None = Field(None, alias="merchantId")
    exchange_rate: float | None = Field(None, alias="exchangeRate")
    operation_date: str | None = Field(None, alias="operationDate")
    source_amount: float | None = Field(None, alias="sourceAmount")
    target_amount: float | None = Field(None, alias="targetAmount")
    source_currency: str | None = Field(None, alias="sourceCurrency")
    target_currency: str | None = Field(None, alias="targetCurrency")
    transactions_start_date: str | None = Field(None, alias="transactionsStartDate")
    transactions_end_date: str | None = Field(None, alias="transactionsEndDate")
    processed_transactions_count: int | None = Field(None, alias="processedTransactionsCount")
    description: str | None = None
    created_at: str | None = Field(None, alias="createdAt")
