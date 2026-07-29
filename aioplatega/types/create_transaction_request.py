from typing import TYPE_CHECKING, Any

from pydantic import Field

from ..enums import PaymentMethodInt
from .base import PlategaObject
from .payment_details import PaymentDetails


class CreateTransactionRequest(PlategaObject):
    """Body for creating a transaction.

    Note:
        Do not supply an ``id``. The API generates the transaction id.

        ``metadata`` carries the payer identifier. Shops in certain categories
        are required to send ``metadata.userId``; where that requirement
        applies, omitting it disables antifraud protection and can get the
        shop suspended. Ask your Platega manager whether it applies to yours.

        ``payment_method`` accepts any integer, not only a
        :class:`~aioplatega.enums.PaymentMethodInt` member. The enum names the
        documented methods, but the GitBook records that ids 1 through 9 are
        P2P and a merchant is enabled for whichever their contract covers, so
        a closed set would lock those merchants out.
    """

    payment_method: PaymentMethodInt | int = Field(alias="paymentMethod")
    payment_details: PaymentDetails = Field(alias="paymentDetails")
    description: str | None = None
    return_url: str | None = Field(None, alias="return")
    failed_url: str | None = Field(None, alias="failedUrl")
    payload: str | None = None
    metadata: dict[str, Any] | None = None

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            payment_method: PaymentMethodInt | int,
            payment_details: PaymentDetails,
            description: str | None = None,
            return_url: str | None = None,
            failed_url: str | None = None,
            payload: str | None = None,
            metadata: dict[str, Any] | None = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            super().__init__(
                payment_method=payment_method,
                payment_details=payment_details,
                description=description,
                return_url=return_url,
                failed_url=failed_url,
                payload=payload,
                metadata=metadata,
                **__pydantic_kwargs,
            )
