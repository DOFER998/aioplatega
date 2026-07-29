from typing import Any, ClassVar

from pydantic import Field

from aioplatega.types import PaymentDetails, PaymentLinkResponse

from .base import PlategaMethod


class CreatePaymentLink(PlategaMethod[PaymentLinkResponse]):
    """POST ``/v2/transaction/process`` — payer chooses the method themselves.

    Unlike :class:`~aioplatega.methods.CreateTransaction`, no payment method is
    fixed up front; the payer picks one on the hosted page.

    Note:
        ``metadata`` carries the payer identifier. Shops in certain categories
        are required to send ``metadata.userId``; where that requirement
        applies, omitting it disables antifraud protection and can get the
        shop suspended. Ask your Platega manager whether it applies to yours.
    """

    __api_method__: ClassVar[str] = "/v2/transaction/process"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = PaymentLinkResponse

    payment_details: PaymentDetails = Field(alias="paymentDetails")
    description: str | None = None
    return_url: str | None = Field(None, alias="return")
    failed_url: str | None = Field(None, alias="failedUrl")
    payload: str | None = None
    metadata: dict[str, Any] | None = None
