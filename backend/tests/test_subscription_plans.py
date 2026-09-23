from sqlalchemy import select

from fastapi.testclient import (
    TestClient,
)

from app.core.security import (
    create_access_token,
    hash_password,
)
from app.models.owner_subscription import (
    OwnerSubscription,
    SubscriptionStatus,
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
    db.commit()
    db.refresh(user)

    return user


def property_payload(
    index: int,
):
    return {
        "name":
            f"Property {index}",
        "address":
            f"{index} Test Street",
        "city":
            "Sidon",
        "country":
            "Lebanon",
    }


def test_admin_can_list_default_plans(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="plans.admin@test.com",
        role=UserRole.ADMIN,
    )

    response = client.get(
        "/api/admin/plans",
        headers=auth_headers(
            admin
        ),
    )

    assert (
        response.status_code
        == 200
    )

    plans = response.json()

    assert [
        plan["code"]
        for plan in plans
    ] == [
        "FREE",
        "STANDARD",
        "PRO",
    ]

    free = plans[0]
    standard = plans[1]
    pro = plans[2]

    assert (
        free["max_properties"]
        == 2
    )

    assert (
        standard["max_properties"]
        == 10
    )

    assert (
        pro["max_properties"]
        is None
    )


def test_non_admin_cannot_manage_plans(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        email="plans.owner@test.com",
        role=UserRole.OWNER,
    )

    response = client.get(
        "/api/admin/plans",
        headers=auth_headers(
            owner
        ),
    )

    assert (
        response.status_code
        == 403
    )


def test_admin_can_create_update_deactivate_and_delete_custom_plan(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="plans.crud@test.com",
        role=UserRole.ADMIN,
    )

    created = client.post(
        "/api/admin/plans",
        headers=auth_headers(
            admin
        ),
        json={
            "code": "BUSINESS",
            "name": "Business",
            "monthly_price": 29,
            "yearly_price": 290,
            "max_properties": 25,
            "sort_order": 40,
            "is_active": True,
        },
    )

    assert (
        created.status_code
        == 201
    )

    plan_id = (
        created.json()["id"]
    )

    updated = client.patch(
        (
            "/api/admin/plans/"
            f"{plan_id}"
        ),
        headers=auth_headers(
            admin
        ),
        json={
            "monthly_price":
                35,
            "max_properties":
                30,
            "is_active":
                False,
        },
    )

    assert (
        updated.status_code
        == 200
    )

    assert (
        updated.json()[
            "is_active"
        ]
        is False
    )

    public = client.get(
        "/api/subscription-plans"
    )

    assert (
        public.status_code
        == 200
    )

    assert "BUSINESS" not in {
        plan["code"]
        for plan
        in public.json()
    }

    deleted = client.delete(
        (
            "/api/admin/plans/"
            f"{plan_id}"
        ),
        headers=auth_headers(
            admin
        ),
    )

    assert (
        deleted.status_code
        == 204
    )


def test_registration_assigns_free_plan(
    client: TestClient,
    db,
):
    response = client.post(
        "/api/auth/register",
        json={
            "email":
                "new.free@test.com",
            "password":
                "OwnerPassword@123",
        },
    )

    assert (
        response.status_code
        == 201
    )

    owner_id = (
        response.json()["id"]
    )

    row = db.execute(
        select(
            OwnerSubscription,
            SubscriptionPlan,
        )
        .join(
            SubscriptionPlan,
            OwnerSubscription.plan_id
            == SubscriptionPlan.id,
        )
        .where(
            OwnerSubscription.owner_id
            == owner_id
        )
    ).one()

    subscription = row[0]
    plan = row[1]

    assert (
        subscription.status
        == SubscriptionStatus.FREE
    )

    assert (
        plan.code
        == "FREE"
    )


def test_free_plan_blocks_third_property(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        email="free.limit@test.com",
        role=UserRole.OWNER,
    )

    first = client.post(
        "/api/properties/",
        headers=auth_headers(
            owner
        ),
        json=property_payload(1),
    )

    second = client.post(
        "/api/properties/",
        headers=auth_headers(
            owner
        ),
        json=property_payload(2),
    )

    third = client.post(
        "/api/properties/",
        headers=auth_headers(
            owner
        ),
        json=property_payload(3),
    )

    assert (
        first.status_code
        == 201
    )

    assert (
        second.status_code
        == 201
    )

    assert (
        third.status_code
        == 409
    )

    assert (
        "Property limit reached"
        in third.json()[
            "detail"
        ]
    )


def test_inactive_plan_still_applies_to_existing_owner(
    client: TestClient,
    db,
):
    ensure_default_plans(db)

    owner = User(
        email=(
            "inactive.plan.owner@test.com"
        ),
        password_hash=(
            hash_password(
                "TestPassword@123"
            )
        ),
        role=UserRole.OWNER,
        is_active=True,
    )

    plan = SubscriptionPlan(
        code="LEGACY",
        name="Legacy",
        monthly_price=5,
        yearly_price=50,
        max_properties=3,
        sort_order=50,
        is_active=False,
    )

    db.add_all(
        [
            owner,
            plan,
        ]
    )
    db.flush()

    db.add(
        OwnerSubscription(
            owner_id=owner.id,
            plan_id=plan.id,
            status=(
                SubscriptionStatus.ACTIVE
            ),
        )
    )

    db.commit()

    for index in range(
        1,
        4,
    ):
        response = client.post(
            "/api/properties/",
            headers=auth_headers(
                owner
            ),
            json=property_payload(
                index,
            ),
        )

        assert (
            response.status_code
            == 201
        )

    blocked = client.post(
        "/api/properties/",
        headers=auth_headers(
            owner
        ),
        json=property_payload(4),
    )

    assert (
        blocked.status_code
        == 409
    )
