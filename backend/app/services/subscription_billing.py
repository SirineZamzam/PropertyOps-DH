from datetime import (
    datetime,
    timezone,
)
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.owner_subscription import (
    BillingInterval,
    OwnerSubscription,
    SubscriptionStatus,
)
from app.models.subscription_payment import (
    SubscriptionPayment,
    SubscriptionPaymentStatus,
)
from app.models.subscription_plan import (
    SubscriptionPlan,
)
from app.models.user import User
from app.services.stripe_service import (
    amount_to_cents,
    get_stripe_client,
)


def create_subscription_checkout(
    *,
    owner: User,
    subscription: OwnerSubscription,
    plan: SubscriptionPlan,
    billing_interval: BillingInterval,
):
    if plan.code == "FREE":
        raise ValueError(
            "FREE does not require Stripe Checkout."
        )

    amount = (
        plan.monthly_price
        if billing_interval
        == BillingInterval.MONTHLY
        else plan.yearly_price
    )

    interval = (
        "month"
        if billing_interval
        == BillingInterval.MONTHLY
        else "year"
    )

    metadata = {
        "flow": "SUBSCRIPTION",
        "owner_id": str(owner.id),
        "plan_id": str(plan.id),
        "billing_interval":
            billing_interval.value,
    }

    client = get_stripe_client()

    params = {
        "mode": "subscription",

        "line_items": [
            {
                "price_data": {
                    "currency":
                        settings.stripe_currency,

                    "product_data": {
                        "name":
                            (
                                "PropertyOps "
                                f"{plan.name}"
                            ),
                    },

                    "unit_amount":
                        amount_to_cents(
                            amount
                        ),

                    "recurring": {
                        "interval":
                            interval,
                    },
                },

                "quantity": 1,
            }
        ],

        "metadata":
            metadata,

        "subscription_data": {
            "metadata":
                metadata,
        },

        "success_url":
            (
                f"{settings.frontend_url}"
                "/app/subscription"
                "?subscription=success"
                "&session_id="
                "{CHECKOUT_SESSION_ID}"
            ),

        "cancel_url":
            (
                f"{settings.frontend_url}"
                "/app/subscription"
                "?subscription=cancelled"
            ),
    }

    if (
        subscription
        .stripe_customer_id
    ):
        params[
            "customer"
        ] = (
            subscription
            .stripe_customer_id
        )
    else:
        params[
            "customer_email"
        ] = owner.email

    return (
        client.v1.checkout.sessions.create(
            params=params
        )
    )


def stripe_object_to_dict(
    value,
) -> dict:
    if value is None:
        return {}

    if isinstance(
        value,
        dict,
    ):
        return value

    if hasattr(
        value,
        "to_dict",
    ):
        return value.to_dict()

    return dict(value)


def timestamp_to_datetime(
    value,
) -> datetime | None:
    if value in (
        None,
        "",
    ):
        return None

    return datetime.fromtimestamp(
        int(value),
        tz=timezone.utc,
    )


def current_period_end_from_subscription(
    subscription_data: dict,
) -> datetime | None:
    direct = subscription_data.get(
        "current_period_end"
    )

    if direct:
        return timestamp_to_datetime(
            direct
        )

    items = (
        (
            subscription_data
            .get("items")
            or {}
        )
        .get("data")
        or []
    )

    if not items:
        return None

    return timestamp_to_datetime(
        items[0].get(
            "current_period_end"
        )
    )


def normalize_subscription_status(
    stripe_status: str | None,
) -> SubscriptionStatus:
    if stripe_status in {
        "active",
        "trialing",
    }:
        return (
            SubscriptionStatus.ACTIVE
        )

    if stripe_status in {
        "past_due",
        "unpaid",
        "paused",
    }:
        return (
            SubscriptionStatus.PAST_DUE
        )

    if stripe_status in {
        "canceled",
        "incomplete_expired",
    }:
        return (
            SubscriptionStatus.CANCELED
        )

    return (
        SubscriptionStatus.INCOMPLETE
    )


def sync_local_subscription_from_stripe(
    *,
    subscription: OwnerSubscription,
    stripe_subscription,
):
    data = stripe_object_to_dict(
        stripe_subscription
    )

    subscription.status = (
        normalize_subscription_status(
            data.get(
                "status"
            )
        )
    )

    subscription.cancel_at_period_end = bool(
        data.get(
            "cancel_at_period_end",
            False,
        )
    )

    subscription.current_period_end = (
        current_period_end_from_subscription(
            data
        )
    )

    metadata = (
        data.get(
            "metadata"
        )
        or {}
    )

    plan_id = metadata.get(
        "plan_id"
    )

    if plan_id:
        subscription.plan_id = int(
            plan_id
        )

    interval = metadata.get(
        "billing_interval"
    )

    if interval:
        subscription.billing_interval = (
            BillingInterval(
                interval
            )
        )

    customer_id = data.get(
        "customer"
    )

    if customer_id:
        subscription.stripe_customer_id = (
            str(customer_id)
        )

    stripe_subscription_id = (
        data.get(
            "id"
        )
    )

    if stripe_subscription_id:
        subscription.stripe_subscription_id = (
            str(
                stripe_subscription_id
            )
        )


def change_stripe_subscription(
    *,
    subscription: OwnerSubscription,
    plan: SubscriptionPlan,
    billing_interval: BillingInterval,
):
    if not (
        subscription
        .stripe_subscription_id
    ):
        raise ValueError(
            "Stripe subscription is missing."
        )

    client = get_stripe_client()

    stripe_subscription = (
        client.v1.subscriptions.retrieve(
            subscription
            .stripe_subscription_id
        )
    )

    data = stripe_object_to_dict(
        stripe_subscription
    )

    items = (
        (
            data.get(
                "items"
            )
            or {}
        )
        .get("data")
        or []
    )

    if not items:
        raise RuntimeError(
            "Stripe subscription has no items."
        )

    current_item = items[0]

    item_id = current_item.get(
        "id"
    )

    price = (
        current_item.get(
            "price"
        )
        or {}
    )

    product = price.get(
        "product"
    )

    if isinstance(
        product,
        dict,
    ):
        product = product.get(
            "id"
        )

    if (
        not item_id
        or not product
    ):
        raise RuntimeError(
            "Stripe subscription item "
            "could not be resolved."
        )

    amount = (
        plan.monthly_price
        if billing_interval
        == BillingInterval.MONTHLY
        else plan.yearly_price
    )

    interval = (
        "month"
        if billing_interval
        == BillingInterval.MONTHLY
        else "year"
    )

    metadata = {
        "flow": "SUBSCRIPTION",
        "owner_id": str(
            subscription.owner_id
        ),
        "plan_id": str(
            plan.id
        ),
        "billing_interval":
            billing_interval.value,
    }

    return (
        client.v1.subscriptions.update(
            subscription
            .stripe_subscription_id,

            params={
                "items": [
                    {
                        "id":
                            item_id,

                        "price_data": {
                            "currency":
                                settings
                                .stripe_currency,

                            "product":
                                str(
                                    product
                                ),

                            "unit_amount":
                                amount_to_cents(
                                    amount
                                ),

                            "recurring": {
                                "interval":
                                    interval,
                            },
                        },

                        "quantity": 1,
                    }
                ],

                "metadata":
                    metadata,

                "cancel_at_period_end":
                    False,

                "proration_behavior":
                    "none",
            },
        )
    )


def set_subscription_cancel_at_period_end(
    *,
    subscription: OwnerSubscription,
    cancel_at_period_end: bool,
):
    if not (
        subscription
        .stripe_subscription_id
    ):
        raise ValueError(
            "Stripe subscription is missing."
        )

    client = get_stripe_client()

    return (
        client.v1.subscriptions.update(
            subscription
            .stripe_subscription_id,

            params={
                "cancel_at_period_end":
                    cancel_at_period_end,
            },
        )
    )


def subscription_id_from_invoice(
    invoice: dict,
) -> str | None:
    direct = invoice.get(
        "subscription"
    )

    if direct:
        return str(direct)

    parent = (
        invoice.get(
            "parent"
        )
        or {}
    )

    details = (
        parent.get(
            "subscription_details"
        )
        or {}
    )

    value = details.get(
        "subscription"
    )

    return (
        str(value)
        if value
        else None
    )


def find_subscription_by_stripe_id(
    db: Session,
    stripe_subscription_id: str | None,
) -> OwnerSubscription | None:
    if not stripe_subscription_id:
        return None

    return db.scalar(
        select(
            OwnerSubscription
        ).where(
            OwnerSubscription
            .stripe_subscription_id
            == stripe_subscription_id
        )
    )


def find_subscription_from_metadata(
    db: Session,
    metadata: dict,
) -> OwnerSubscription | None:
    owner_id = metadata.get(
        "owner_id"
    )

    if not owner_id:
        return None

    try:
        owner_id_int = int(
            owner_id
        )
    except (
        TypeError,
        ValueError,
    ):
        return None

    return db.scalar(
        select(
            OwnerSubscription
        ).where(
            OwnerSubscription.owner_id
            == owner_id_int
        )
    )


def upsert_subscription_payment(
    *,
    db: Session,
    subscription: OwnerSubscription,
    invoice: dict,
    payment_status:
        SubscriptionPaymentStatus,
):
    invoice_id = invoice.get(
        "id"
    )

    if not invoice_id:
        return

    existing = db.scalar(
        select(
            SubscriptionPayment
        ).where(
            SubscriptionPayment
            .stripe_invoice_id
            == invoice_id
        )
    )

    amount_cents = (
        invoice.get(
            "amount_paid"
        )
        if payment_status
        == SubscriptionPaymentStatus.PAID
        else invoice.get(
            "amount_due"
        )
    )

    if amount_cents is None:
        amount_cents = 0

    amount = (
        Decimal(
            str(amount_cents)
        )
        / Decimal("100")
    )

    currency = (
        invoice.get(
            "currency"
        )
        or settings.stripe_currency
    )

    if existing:
        existing.status = (
            payment_status
        )
        existing.amount = amount
        existing.currency = currency
        existing.plan_id = (
            subscription.plan_id
        )
        return

    db.add(
        SubscriptionPayment(
            owner_subscription_id=(
                subscription.id
            ),
            owner_id=(
                subscription.owner_id
            ),
            plan_id=(
                subscription.plan_id
            ),
            stripe_invoice_id=(
                str(invoice_id)
            ),
            amount=amount,
            currency=currency,
            status=(
                payment_status
            ),
        )
    )


def handle_subscription_event(
    *,
    db: Session,
    event_type: str,
    event_object: dict,
) -> bool:
    if (
        event_type
        == "checkout.session.completed"
        and (
            event_object.get(
                "metadata",
                {},
            ).get("flow")
            == "SUBSCRIPTION"
        )
    ):
        metadata = (
            event_object.get(
                "metadata"
            )
            or {}
        )

        subscription = (
            find_subscription_from_metadata(
                db,
                metadata,
            )
        )

        if subscription is None:
            return True

        plan_id = metadata.get(
            "plan_id"
        )

        billing_interval = (
            metadata.get(
                "billing_interval"
            )
        )

        if plan_id:
            subscription.plan_id = int(
                plan_id
            )

        if billing_interval:
            subscription.billing_interval = (
                BillingInterval(
                    billing_interval
                )
            )

        customer_id = event_object.get(
            "customer"
        )

        stripe_subscription_id = (
            event_object.get(
                "subscription"
            )
        )

        if customer_id:
            subscription.stripe_customer_id = (
                str(customer_id)
            )

        if stripe_subscription_id:
            subscription.stripe_subscription_id = (
                str(
                    stripe_subscription_id
                )
            )

        if subscription.status not in {
             SubscriptionStatus.ACTIVE,
             SubscriptionStatus.PAST_DUE,
             SubscriptionStatus.CANCELED, 
           }:
               subscription.status = (
                  SubscriptionStatus.INCOMPLETE
                )

        return True

    if event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        stripe_subscription_id = (
            event_object.get(
                "id"
            )
        )

        metadata = (
            event_object.get(
                "metadata"
            )
            or {}
        )

        subscription = (
            find_subscription_by_stripe_id(
                db,
                str(
                    stripe_subscription_id
                )
                if stripe_subscription_id
                else None,
            )
            or
            find_subscription_from_metadata(
                db,
                metadata,
            )
        )

        if subscription is None:
            return True

        if stripe_subscription_id:
            subscription.stripe_subscription_id = (
                str(
                    stripe_subscription_id
                )
            )

        customer_id = event_object.get(
            "customer"
        )

        if customer_id:
            subscription.stripe_customer_id = (
                str(customer_id)
            )

        plan_id = metadata.get(
            "plan_id"
        )

        if plan_id:
            subscription.plan_id = int(
                plan_id
            )

        billing_interval = (
            metadata.get(
                "billing_interval"
            )
        )

        if billing_interval:
            subscription.billing_interval = (
                BillingInterval(
                    billing_interval
                )
            )

        if (
            event_type
            == "customer.subscription.deleted"
        ):
            subscription.status = (
                SubscriptionStatus.CANCELED
            )
        else:
            subscription.status = (
                normalize_subscription_status(
                    event_object.get(
                        "status"
                    )
                )
            )

        subscription.current_period_end = (
            current_period_end_from_subscription(
                event_object
            )
        )

        subscription.cancel_at_period_end = bool(
            event_object.get(
                "cancel_at_period_end",
                False,
            )
        )

        return True

    if event_type in {
        "invoice.paid",
        "invoice.payment_failed",
    }:
        stripe_subscription_id = (
            subscription_id_from_invoice(
                event_object
            )
        )

        subscription = (
            find_subscription_by_stripe_id(
                db,
                stripe_subscription_id,
            )
        )

        if subscription is None:
            return True

        if (
            event_type
            == "invoice.paid"
        ):
            subscription.status = (
                SubscriptionStatus.ACTIVE
            )

            upsert_subscription_payment(
                db=db,
                subscription=subscription,
                invoice=event_object,
                payment_status=(
                    SubscriptionPaymentStatus.PAID
                ),
            )
        else:
            subscription.status = (
                SubscriptionStatus.PAST_DUE
            )

            upsert_subscription_payment(
                db=db,
                subscription=subscription,
                invoice=event_object,
                payment_status=(
                    SubscriptionPaymentStatus.FAILED
                ),
            )

        return True

    return False
