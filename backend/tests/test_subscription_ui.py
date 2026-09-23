from datetime import (
    datetime,
    timezone,
)
from decimal import Decimal

from fastapi.testclient import (
    TestClient,
)
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


def make_user(
    db,
    *,
    email: str,
    role: UserRole,
):
    user = User(
        email=email,
        password_hash=hash_password(
            "TestPassword@123"
        ),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.flush()

    return user


def plan(
    db,
    code: str,
) -> SubscriptionPlan:
    ensure_default_plans(db)

    result = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.code
            == code
        )
    )

    assert result is not None

    return result


def make_subscription(
    db,
    *,
    owner: User,
    plan_code: str = "FREE",
    status:
        SubscriptionStatus = (
            SubscriptionStatus.FREE
        ),
    stripe_subscription_id:
        str | None = None,
):
    selected_plan = plan(
        db,
        plan_code,
    )

    subscription = OwnerSubscription(
        owner_id=owner.id,
        plan_id=selected_plan.id,
        status=status,
        billing_interval=(
            BillingInterval.MONTHLY
            if plan_code != "FREE"
            else None
        ),
        stripe_customer_id=(
            f"cus_test_{owner.id}"
            if stripe_subscription_id
            else None
        ),
        stripe_subscription_id=(
            stripe_subscription_id
        ),
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def test_owner_subscription_includes_usage_and_effective_limit(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        email="owner.ui@test.com",
        role=UserRole.OWNER,
    )

    make_subscription(
        db,
        owner=owner,
    )

    response = client.get(
        "/api/owner/subscription",
        headers=auth_headers(
            owner
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["plan"]["code"]
        == "FREE"
    )

    assert (
        body[
            "effective_max_properties"
        ]
        == 2
    )


def test_owner_payment_history_is_scoped(
    client: TestClient,
    db,
):
    owner_a = make_user(
        db,
        email="owner.a.payments@test.com",
        role=UserRole.OWNER,
    )

    owner_b = make_user(
        db,
        email="owner.b.payments@test.com",
        role=UserRole.OWNER,
    )

    subscription_a = (
        make_subscription(
            db,
            owner=owner_a,
            plan_code="STANDARD",
            status=(
                SubscriptionStatus.ACTIVE
            ),
            stripe_subscription_id=(
                "sub_owner_a"
            ),
        )
    )

    subscription_b = (
        make_subscription(
            db,
            owner=owner_b,
            plan_code="PRO",
            status=(
                SubscriptionStatus.ACTIVE
            ),
            stripe_subscription_id=(
                "sub_owner_b"
            ),
        )
    )

    standard = plan(
        db,
        "STANDARD",
    )

    pro = plan(
        db,
        "PRO",
    )

    db.add_all(
        [
            SubscriptionPayment(
                owner_subscription_id=(
                    subscription_a.id
                ),
                owner_id=owner_a.id,
                plan_id=standard.id,
                stripe_invoice_id=(
                    "in_owner_a"
                ),
                amount=Decimal(
                    "9.00"
                ),
                currency="usd",
                status=(
                    SubscriptionPaymentStatus.PAID
                ),
            ),
            SubscriptionPayment(
                owner_subscription_id=(
                    subscription_b.id
                ),
                owner_id=owner_b.id,
                plan_id=pro.id,
                stripe_invoice_id=(
                    "in_owner_b"
                ),
                amount=Decimal(
                    "19.00"
                ),
                currency="usd",
                status=(
                    SubscriptionPaymentStatus.PAID
                ),
            ),
        ]
    )

    db.commit()

    response = client.get(
        "/api/owner/subscription/payments",
        headers=auth_headers(
            owner_a
        ),
    )

    assert (
        response.status_code
        == 200
    )

    items = response.json()

    assert len(items) == 1

    assert (
        items[0][
            "stripe_invoice_id"
        ]
        == "in_owner_a"
    )


def test_owner_can_change_active_paid_plan(
    client: TestClient,
    db,
    monkeypatch,
):
    owner = make_user(
        db,
        email="owner.change@test.com",
        role=UserRole.OWNER,
    )

    subscription = (
        make_subscription(
            db,
            owner=owner,
            plan_code="STANDARD",
            status=(
                SubscriptionStatus.ACTIVE
            ),
            stripe_subscription_id=(
                "sub_change"
            ),
        )
    )

    pro = plan(
        db,
        "PRO",
    )

    def fake_change(
        *,
        subscription,
        plan,
        billing_interval,
    ):
        return {
            "id":
                "sub_change",
            "status":
                "active",
            "customer":
                "cus_test",
            "cancel_at_period_end":
                False,
            "metadata": {
                "plan_id":
                    str(plan.id),
                "billing_interval":
                    billing_interval.value,
            },
            "items": {
                "data": [
                    {
                        "current_period_end":
                            1893456000,
                    }
                ]
            },
        }

    monkeypatch.setattr(
        (
            "app.api.routes."
            "subscription_billing."
            "change_stripe_subscription"
        ),
        fake_change,
    )

    response = client.post(
        "/api/owner/subscription/change",
        headers=auth_headers(
            owner
        ),
        json={
            "plan_id":
                pro.id,
            "billing_interval":
                "YEARLY",
        },
    )

    assert (
        response.status_code
        == 200
    )

    db.refresh(subscription)

    assert (
        subscription.plan_id
        == pro.id
    )

    assert (
        subscription.billing_interval
        == BillingInterval.YEARLY
    )

    assert (
        subscription.status
        == SubscriptionStatus.ACTIVE
    )


def test_owner_can_schedule_and_resume_cancellation(
    client: TestClient,
    db,
    monkeypatch,
):
    owner = make_user(
        db,
        email="owner.cancel@test.com",
        role=UserRole.OWNER,
    )

    subscription = (
        make_subscription(
            db,
            owner=owner,
            plan_code="STANDARD",
            status=(
                SubscriptionStatus.ACTIVE
            ),
            stripe_subscription_id=(
                "sub_cancel_ui"
            ),
        )
    )

    def fake_cancel(
        *,
        subscription,
        cancel_at_period_end,
    ):
        return {
            "id":
                "sub_cancel_ui",
            "status":
                "active",
            "customer":
                "cus_test",
            "cancel_at_period_end":
                cancel_at_period_end,
            "metadata": {
                "plan_id":
                    str(
                        subscription.plan_id
                    ),
                "billing_interval":
                    "MONTHLY",
            },
            "items": {
                "data": [
                    {
                        "current_period_end":
                            1893456000,
                    }
                ]
            },
        }

    monkeypatch.setattr(
        (
            "app.api.routes."
            "subscription_billing."
            "set_subscription_cancel_at_period_end"
        ),
        fake_cancel,
    )

    cancel = client.post(
        "/api/owner/subscription/cancel",
        headers=auth_headers(
            owner
        ),
    )

    assert (
        cancel.status_code
        == 200
    )

    db.refresh(subscription)

    assert (
        subscription
        .cancel_at_period_end
        is True
    )

    resume = client.post(
        "/api/owner/subscription/resume",
        headers=auth_headers(
            owner
        ),
    )

    assert (
        resume.status_code
        == 200
    )

    db.refresh(subscription)

    assert (
        subscription
        .cancel_at_period_end
        is False
    )


def test_cancelled_checkout_returns_owner_to_free(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        email="owner.checkout.cancel@test.com",
        role=UserRole.OWNER,
    )

    subscription = (
        make_subscription(
            db,
            owner=owner,
            plan_code="STANDARD",
            status=(
                SubscriptionStatus.INCOMPLETE
            ),
        )
    )

    response = client.post(
        (
            "/api/owner/subscription/"
            "checkout-cancelled"
        ),
        headers=auth_headers(
            owner
        ),
    )

    assert (
        response.status_code
        == 200
    )

    db.refresh(subscription)

    free = plan(
        db,
        "FREE",
    )

    assert (
        subscription.plan_id
        == free.id
    )

    assert (
        subscription.status
        == SubscriptionStatus.FREE
    )


def test_admin_subscription_views_require_admin_and_show_data(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="admin.subs@test.com",
        role=UserRole.ADMIN,
    )

    owner = make_user(
        db,
        email="owner.admin.subs@test.com",
        role=UserRole.OWNER,
    )

    subscription = (
        make_subscription(
            db,
            owner=owner,
            plan_code="STANDARD",
            status=(
                SubscriptionStatus.ACTIVE
            ),
            stripe_subscription_id=(
                "sub_admin_view"
            ),
        )
    )

    standard = plan(
        db,
        "STANDARD",
    )

    db.add(
        SubscriptionPayment(
            owner_subscription_id=(
                subscription.id
            ),
            owner_id=owner.id,
            plan_id=standard.id,
            stripe_invoice_id=(
                "in_admin_view"
            ),
            amount=Decimal(
                "9.00"
            ),
            currency="usd",
            status=(
                SubscriptionPaymentStatus.PAID
            ),
            created_at=datetime.now(
                timezone.utc
            ),
        )
    )

    db.commit()

    subscriptions = client.get(
        "/api/admin/subscriptions",
        headers=auth_headers(
            admin
        ),
    )

    payments = client.get(
        (
            "/api/admin/"
            "subscription-payments"
        ),
        headers=auth_headers(
            admin
        ),
    )

    denied = client.get(
        "/api/admin/subscriptions",
        headers=auth_headers(
            owner
        ),
    )

    assert (
        subscriptions.status_code
        == 200
    )

    assert (
        subscriptions.json()[
            "meta"
        ]["total"]
        == 1
    )

    assert (
        payments.status_code
        == 200
    )

    assert (
        payments.json()[
            "items"
        ][0][
            "stripe_invoice_id"
        ]
        == "in_admin_view"
    )

    assert (
        denied.status_code
        == 403
    )
