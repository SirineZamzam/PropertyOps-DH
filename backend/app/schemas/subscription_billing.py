from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.owner_subscription import (
    BillingInterval,
    SubscriptionStatus,
)
from app.models.subscription_payment import (
    SubscriptionPaymentStatus,
)


class SubscriptionCheckoutRequest(
    BaseModel
):
    plan_id: int
    billing_interval: BillingInterval


class SubscriptionCheckoutResponse(
    BaseModel
):
    checkout_url: str


class SubscriptionBillingRead(
    BaseModel
):
    status: SubscriptionStatus
    billing_interval: BillingInterval | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    stripe_subscription_id: str | None


class SubscriptionPaymentRead(
    BaseModel
):
    id: int
    owner_id: int
    plan_id: int
    stripe_invoice_id: str
    amount: Decimal
    currency: str
    status: SubscriptionPaymentStatus
    created_at: datetime
