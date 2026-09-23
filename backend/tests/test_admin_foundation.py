from datetime import date
from decimal import Decimal

from fastapi.testclient import (
    TestClient,
)

from app.core.security import (
    create_access_token,
    hash_password,
)
from app.models.building import Building
from app.models.lease import (
    Lease,
    LeaseStatus,
)
from app.models.property import Property
from app.models.unit import (
    Unit,
    UnitStatus,
)
from app.models.user import (
    User,
    UserRole,
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
    active: bool = True,
):
    user = User(
        email=email,
        password_hash=hash_password(
            "TestPassword@123"
        ),
        role=role,
        is_active=active,
    )

    db.add(user)
    db.flush()

    return user


def create_owner_portfolio(
    db,
    *,
    owner: User,
    tenant: User,
):
    property_record = Property(
        owner_id=owner.id,
        name="Admin Test Property",
        address="1 Test Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(property_record)
    db.flush()

    building = Building(
        property_id=(
            property_record.id
        ),
        name="Main",
    )

    db.add(building)
    db.flush()

    unit = Unit(
        building_id=building.id,
        unit_number="101",
        status=UnitStatus.OCCUPIED,
    )

    db.add(unit)
    db.flush()

    lease = Lease(
        unit_id=unit.id,
        tenant_user_id=tenant.id,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        rent_amount=Decimal(
            "900.00"
        ),
        status=LeaseStatus.ACTIVE,
    )

    db.add(lease)
    db.commit()


def test_admin_overview_requires_admin(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="admin@test.com",
        role=UserRole.ADMIN,
    )

    owner = make_user(
        db,
        email="owner@test.com",
        role=UserRole.OWNER,
    )

    db.commit()

    allowed = client.get(
        "/api/admin/overview",
        headers=auth_headers(
            admin
        ),
    )

    denied = client.get(
        "/api/admin/overview",
        headers=auth_headers(
            owner
        ),
    )

    assert (
        allowed.status_code
        == 200
    )

    assert (
        denied.status_code
        == 403
    )


def test_admin_owner_list_only_returns_owners(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="admin.list@test.com",
        role=UserRole.ADMIN,
    )

    owner = make_user(
        db,
        email="owner.list@test.com",
        role=UserRole.OWNER,
    )

    tenant = make_user(
        db,
        email="tenant.list@test.com",
        role=UserRole.TENANT,
    )

    create_owner_portfolio(
        db,
        owner=owner,
        tenant=tenant,
    )

    response = client.get(
        "/api/admin/owners",
        headers=auth_headers(
            admin
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["meta"]["total"]
        == 1
    )

    assert (
        len(body["items"])
        == 1
    )

    item = body["items"][0]

    assert (
        item["id"]
        == owner.id
    )

    assert (
        item["property_count"]
        == 1
    )

    assert (
        item["building_count"]
        == 1
    )

    assert (
        item["unit_count"]
        == 1
    )

    assert (
        item["active_lease_count"]
        == 1
    )


def test_admin_owner_search_and_status_filter(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="admin.filters@test.com",
        role=UserRole.ADMIN,
    )

    active_owner = make_user(
        db,
        email="alpha.owner@test.com",
        role=UserRole.OWNER,
        active=True,
    )

    inactive_owner = make_user(
        db,
        email="beta.owner@test.com",
        role=UserRole.OWNER,
        active=False,
    )

    db.commit()

    search_response = (
        client.get(
            (
                "/api/admin/owners"
                "?search=alpha"
            ),
            headers=auth_headers(
                admin
            ),
        )
    )

    inactive_response = (
        client.get(
            (
                "/api/admin/owners"
                "?active=false"
            ),
            headers=auth_headers(
                admin
            ),
        )
    )

    assert (
        search_response
        .status_code
        == 200
    )

    assert (
        search_response
        .json()["items"][0][
            "id"
        ]
        == active_owner.id
    )

    assert (
        inactive_response
        .status_code
        == 200
    )

    assert (
        inactive_response
        .json()["items"][0][
            "id"
        ]
        == inactive_owner.id
    )


def test_admin_can_deactivate_owner_and_login_is_blocked(
    client: TestClient,
    db,
):
    admin = make_user(
        db,
        email="admin.status@test.com",
        role=UserRole.ADMIN,
    )

    owner = User(
        email="owner.status@test.com",
        password_hash=hash_password(
            "OwnerPassword@123"
        ),
        role=UserRole.OWNER,
        is_active=True,
    )

    db.add(owner)
    db.commit()

    response = client.patch(
        (
            "/api/admin/owners/"
            f"{owner.id}/status"
        ),
        headers=auth_headers(
            admin
        ),
        json={
            "is_active": False,
        },
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "is_active"
        ]
        is False
    )

    login = client.post(
        "/api/auth/login",
        json={
            "email":
                owner.email,
            "password":
                "OwnerPassword@123",
        },
    )

    assert (
        login.status_code
        == 403
    )


def test_owner_cannot_change_other_owner_status(
    client: TestClient,
    db,
):
    owner_a = make_user(
        db,
        email="owner.a.admin@test.com",
        role=UserRole.OWNER,
    )

    owner_b = make_user(
        db,
        email="owner.b.admin@test.com",
        role=UserRole.OWNER,
    )

    db.commit()

    response = client.patch(
        (
            "/api/admin/owners/"
            f"{owner_b.id}/status"
        ),
        headers=auth_headers(
            owner_a
        ),
        json={
            "is_active": False,
        },
    )

    assert (
        response.status_code
        == 403
    )
