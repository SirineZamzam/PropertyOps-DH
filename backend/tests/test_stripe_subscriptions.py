from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import (
    create_access_token,
    hash_password,
)
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
from app.models.user import (
    User,
    UserRole,
)
from app.services.subscription_billing import (
    handle_subscription_event,
)
from app.services.subscriptions import (
    ensure_default_plans,
)


def auth_headers(
    user: User,
):
    return {
        "Authorization":
            (
                "Bearer "
                + create_access_token(
                    user.id
                )
            )
    }


def make_owner(db):
    ensure_default_plans(db)

    owner = User(
        email="stripe.owner@test.com",
        password_hash=hash_password(
            "TestPassword@123"
        ),
        role=UserRole.OWNER,
        is_active=True,
    )

    db.add(owner)
    db.flush()

    free = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.code
            == "FREE"
        )
    )

    subscription = OwnerSubscription(
        owner_id=owner.id,
        plan_id=free.id,
        status=(
            SubscriptionStatus.FREE
        ),
    )

    db.add(subscription)
    db.commit()

    return owner, subscription


def paid_plan(db):
    ensure_default_plans(db)

    return db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.code
            == "STANDARD"
        )
    )


def test_subscription_checkout_endpoint_uses_stripe(
    client: TestClient,
    db,
    monkeypatch,
):
    owner, _ = make_owner(db)
    plan = paid_plan(db)

    monkeypatch.setattr(
        (
            "app.api.routes."
            "subscription_billing."
            "create_subscription_checkout"
        ),
        lambda **kwargs:
            SimpleNamespace(
                url=(
                    "https://checkout."
                    "stripe.test/session"
                ),
            ),
    )

    response = client.post(
        "/api/owner/subscription/checkout",
        headers=auth_headers(
            owner
        ),
        json={
            "plan_id": plan.id,
            "billing_interval":
                "MONTHLY",
        },
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "checkout_url"
        ]
        == (
            "https://checkout."
            "stripe.test/session"
        )
    )

    subscription = db.scalar(
        select(
            OwnerSubscription
        ).where(
            OwnerSubscription.owner_id
            == owner.id
        )
    )

    assert (
        subscription.status
        == SubscriptionStatus.INCOMPLETE
    )

    assert (
        subscription.plan_id
        == plan.id
    )


def test_subscription_checkout_rejects_free_plan(
    client: TestClient,
    db,
):
    owner, _ = make_owner(db)

    free = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.code
            == "FREE"
        )
    )

    response = client.post(
        "/api/owner/subscription/checkout",
        headers=auth_headers(
            owner
        ),
        json={
            "plan_id": free.id,
            "billing_interval":
                "MONTHLY",
        },
    )

    assert (
        response.status_code
        == 409
    )


def test_checkout_completed_links_stripe_subscription(
    db,
):
    owner, subscription = (
        make_owner(db)
    )

    plan = paid_plan(db)

    handled = (
        handle_subscription_event(
            db=db,
            event_type=(
                "checkout.session.completed"
            ),
            event_object={
                "metadata": {
                    "flow":
                        "SUBSCRIPTION",
                    "owner_id":
                        str(owner.id),
                    "plan_id":
                        str(plan.id),
                    "billing_interval":
                        "YEARLY",
                },
                "customer":
                    "cus_test_123",
                "subscription":
                    "sub_test_123",
            },
        )
    )

    db.commit()
    db.refresh(subscription)

    assert handled is True

    assert (
        subscription
        .stripe_customer_id
        == "cus_test_123"
    )

    assert (
        subscription
        .stripe_subscription_id
        == "sub_test_123"
    )

    assert (
        subscription.billing_interval
        == BillingInterval.YEARLY
    )


def test_invoice_paid_activates_and_records_payment(
    db,
):
    owner, subscription = (
        make_owner(db)
    )

    plan = paid_plan(db)

    subscription.plan_id = (
        plan.id
    )

    subscription.status = (
        SubscriptionStatus.INCOMPLETE
    )

    subscription.stripe_subscription_id = (
        "sub_paid_123"
    )

    db.commit()

    handled = (
        handle_subscription_event(
            db=db,
            event_type="invoice.paid",
            event_object={
                "id":
                    "in_paid_123",
                "subscription":
                    "sub_paid_123",
                "amount_paid":
                    900,
                "currency":
                    "usd",
            },
        )
    )

    db.commit()
    db.refresh(subscription)

    assert handled is True

    assert (
        subscription.status
        == SubscriptionStatus.ACTIVE
    )

    payment = db.scalar(
        select(
            SubscriptionPayment
        ).where(
            SubscriptionPayment
            .stripe_invoice_id
            == "in_paid_123"
        )
    )

    assert payment is not None

    assert (
        payment.status
        == SubscriptionPaymentStatus.PAID
    )

    assert float(
        payment.amount
    ) == 9.0


def test_invoice_failed_marks_past_due(
    db,
):
    _, subscription = (
        make_owner(db)
    )

    plan = paid_plan(db)

    subscription.plan_id = (
        plan.id
    )

    subscription.status = (
        SubscriptionStatus.ACTIVE
    )

    subscription.stripe_subscription_id = (
        "sub_failed_123"
    )

    db.commit()

    handle_subscription_event(
        db=db,
        event_type=(
            "invoice.payment_failed"
        ),
        event_object={
            "id":
                "in_failed_123",
            "subscription":
                "sub_failed_123",
            "amount_due":
                900,
            "currency":
                "usd",
        },
    )

    db.commit()
    db.refresh(subscription)

    assert (
        subscription.status
        == SubscriptionStatus.PAST_DUE
    )


def test_subscription_deleted_marks_canceled(
    db,
):
    owner, subscription = (
        make_owner(db)
    )

    plan = paid_plan(db)

    subscription.plan_id = (
        plan.id
    )

    subscription.status = (
        SubscriptionStatus.ACTIVE
    )

    subscription.stripe_subscription_id = (
        "sub_cancel_123"
    )

    db.commit()

    handle_subscription_event(
        db=db,
        event_type=(
            "customer.subscription.deleted"
        ),
        event_object={
            "id":
                "sub_cancel_123",
            "customer":
                "cus_cancel_123",
            "status":
                "canceled",
            "metadata": {
                "owner_id":
                    str(owner.id),
                "plan_id":
                    str(plan.id),
                "billing_interval":
                    "MONTHLY",
            },
            "cancel_at_period_end":
                False,
        },
    )

    db.commit()
    db.refresh(subscription)

    assert (
        subscription.status
        == SubscriptionStatus.CANCELED
    )

def test_late_checkout_event_does_not_downgrade_active_subscription(
    db,
):
    owner, subscription = (
        make_owner(db)
    )

    plan = paid_plan(db)

    subscription.plan_id = (
        plan.id
    )
    subscription.status = (
        SubscriptionStatus.ACTIVE
    )
    subscription.stripe_subscription_id = (
        "sub_out_of_order"
    )

    db.commit()

    handled = handle_subscription_event(
        db=db,
        event_type=(
            "checkout.session.completed"
        ),
        event_object={
            "metadata": {
                "flow":
                    "SUBSCRIPTION",
                "owner_id":
                    str(owner.id),
                "plan_id":
                    str(plan.id),
                "billing_interval":
                    "MONTHLY",
            },
            "customer":
                "cus_out_of_order",
            "subscription":
                "sub_out_of_order",
        },
    )

    db.commit()
    db.refresh(subscription)

    assert handled is True

    assert (
        subscription.status
        == SubscriptionStatus.ACTIVE
    )