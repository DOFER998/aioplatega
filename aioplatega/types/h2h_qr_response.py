from pydantic import Field

from .base import PlategaObject


class H2HQrResponse(PlategaObject):
    """Payment details for a host-to-host transaction.

    Note:
        The shape depends on the method. The Apidog docs show an SBP QR
        (:attr:`amount` and :attr:`qr`); the older GitBook shows P2P bank
        requisites (:attr:`account_number`, :attr:`account_name`,
        :attr:`method`). Every field is optional so either answer parses.
    """

    amount: float | None = None
    qr: str | None = None
    account_number: str | None = Field(None, alias="accountNumber")
    masked_account_number: str | None = Field(None, alias="maskedAccountNumber")
    account_name: str | None = Field(None, alias="accountName")
    method: str | None = None
