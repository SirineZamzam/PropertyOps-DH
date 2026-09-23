from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    EmailStr,
)

from app.models.owner_subscription import (
    BillingInterval,
    SubscriptionStatus,
)
from app.models.subscription_payment import (
    SubscriptionPaymentStatus,
)


class SubscriptionChangeRequest(
    BaseModel
):
    plan_id: int
    billing_interval: BillingInterval


class SubscriptionActionRead(
    BaseModel
):
    message: str


class SubscriptionPaymentItemRead(
    BaseModel
):
    id: int
    plan_id: int
    plan_code: str
    plan_name: str

    stripe_invoice_id: str
    amount: Decimal
    currency: str
    status: SubscriptionPaymentStatus
    created_at: datetime


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class AdminSubscriptionSummaryRead(
    BaseModel
):
    total: int
    free: int
    active_paid: int
    incomplete: int
    past_due: int
    canceled: int


class AdminSubscriptionItemRead(
    BaseModel
):
    owner_id: int
    owner_email: EmailStr
    owner_first_name: str | None
    owner_last_name: str | None
    owner_is_active: bool

    plan_id: int
    plan_code: str
    plan_name: str

    status: SubscriptionStatus
    billing_interval: BillingInterval | None

    property_count: int
    max_properties: int | None

    current_period_end: datetime | None
    cancel_at_period_end: bool


class AdminSubscriptionPage(
    BaseModel
):
    items: list[
        AdminSubscriptionItemRead
    ]

    meta: PageMeta


class AdminSubscriptionPaymentItemRead(
    BaseModel
):
    id: int

    owner_id: int
    owner_email: EmailStr
    owner_first_name: str | None
    owner_last_name: str | None

    plan_id: int
    plan_code: str
    plan_name: str

    stripe_invoice_id: str
    amount: Decimal
    currency: str
    status: SubscriptionPaymentStatus
    created_at: datetime


class AdminSubscriptionPaymentPage(
    BaseModel
):
    items: list[
        AdminSubscriptionPaymentItemRead
    ]

    meta: PageMeta
