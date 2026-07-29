"""Recurring SBP subscriptions."""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from aioplatega.types import (
    CancelSubscriptionResponse,
    CreateSubscriptionResponse,
    PaymentDetails,
    Subscription,
    SubscriptionListResponse,
)

from .base import PlategaMethod

SUBSCRIPTION_PAYMENT_METHOD = 6
"""The method id that turns ``/transaction/process`` into a subscription.

Deliberately not a :class:`~aioplatega.enums.PaymentMethodInt` member: the
published enum does not contain 6, it is documented only as "always 6" for
this one endpoint.
"""


class CreateSubscription(PlategaMethod[CreateSubscriptionResponse]):
    """POST ``/transaction/process`` with the subscription payment method.

    The ``transaction_id`` in the response is the subscription id.
    """

    __api_method__: ClassVar[str] = "/transaction/process"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = CreateSubscriptionResponse

    payment_method: int = Field(SUBSCRIPTION_PAYMENT_METHOD, alias="paymentMethod")
    payment_details: PaymentDetails = Field(alias="paymentDetails")
    description: str | None = None


class GetSubscription(PlategaMethod[Subscription]):
    """GET ``/subscription/{subscriptionId}``."""

    __api_method__: ClassVar[str] = "/subscription/{subscription_id}"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = Subscription

    subscription_id: UUID = Field(alias="subscriptionId")


class ListSubscriptions(PlategaMethod[SubscriptionListResponse]):
    """GET ``/subscription`` — a filtered, paginated list."""

    __api_method__: ClassVar[str] = "/subscription"
    __http_method__: ClassVar[str] = "GET"
    __returning__: ClassVar[type] = SubscriptionListResponse

    status: str | None = None
    from_date: str | None = Field(None, alias="from")
    to_date: str | None = Field(None, alias="to")
    page: int | None = None
    size: int | None = None


class CancelSubscription(PlategaMethod[CancelSubscriptionResponse]):
    """POST ``/subscription/{subscriptionId}/cancel``. Idempotent.

    Sent without a body. The published docs show a create-transaction body on
    this endpoint, which is the create schema repeated verbatim and reads as a
    documentation copy-paste rather than a real requirement.
    """

    __api_method__: ClassVar[str] = "/subscription/{subscription_id}/cancel"
    __http_method__: ClassVar[str] = "POST"
    __returning__: ClassVar[type] = CancelSubscriptionResponse

    subscription_id: UUID = Field(alias="subscriptionId")
