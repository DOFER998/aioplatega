from pydantic import Field

from .base import PlategaObject


class PaymentMetadata(PlategaObject):
    """Payer identification sent alongside a payment.

    Shops in certain categories are required to send this. Where the
    requirement applies, omitting ``user_id`` disables antifraud protection
    and can get the shop suspended. Ask your Platega manager whether it
    applies to yours.

    Note:
        The schema marks both fields required, but they are optional here so
        that a shop holding only one of them can still send it. Extra keys are
        preserved, so anything your shop additionally needs can be passed.
    """

    user_id: str | None = Field(None, alias="userId")
    user_name: str | None = Field(None, alias="userName")
