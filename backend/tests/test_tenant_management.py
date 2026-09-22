from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.security import (
    create_access_token,
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
    first_name: str,
    last_name: str,
):
    user = User(
        email=email,
        password_hash="test-hash",
        role=role,
        first_name=first_name,
        last_name=last_name,
        phone_number="+961 70 111 222",
    )

    db.add(user)
    db.flush()

    return user


def make_home(
    db,
    *,
    owner: User,
    tenant: User,
    suffix: str,
    lease_status: LeaseStatus,
):
    property_record = Property(
        owner_id=owner.id,
        name=f"Property {suffix}",
        address="1 Test Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(property_record)
    db.flush()

    building = Building(
        property_id=property_record.id,
        name=f"Building {suffix}",
    )

    db.add(building)
    db.flush()

    unit = Unit(
        building_id=building.id,
        unit_number=suffix,
        status=(
            UnitStatus.OCCUPIED
            if lease_status
            == LeaseStatus.ACTIVE
            else UnitStatus.VACANT
        ),
    )

    db.add(unit)
    db.flush()

    lease = Lease(
        unit_id=unit.id,
        tenant_user_id=tenant.id,
        start_date=date(
            2026,
            1,
            1,
        ),
        end_date=date(
            2027,
            1,
            1,
        ),
        rent_amount=Decimal(
            "800.00"
        ),
        status=lease_status,
    )

    db.add(lease)
    db.commit()

    return {
        "property":
            property_record,
        "building": building,
        "unit": unit,
        "lease": lease,
    }


def test_owner_current_tenants_are_scoped_to_owned_active_leases(
    client: TestClient,
    db,
):
    owner_a = make_user(
        db,
        email="owner.a.tenants@test.com",
        role=UserRole.OWNER,
        first_name="Owner",
        last_name="A",
    )

    owner_b = make_user(
        db,
        email="owner.b.tenants@test.com",
        role=UserRole.OWNER,
        first_name="Owner",
        last_name="B",
    )

    shared_tenant = make_user(
        db,
        email="shared.tenant@test.com",
        role=UserRole.TENANT,
        first_name="Shared",
        last_name="Tenant",
    )

    old_tenant = make_user(
        db,
        email="old.tenant@test.com",
        role=UserRole.TENANT,
        first_name="Old",
        last_name="Tenant",
    )

    home_a = make_home(
        db,
        owner=owner_a,
        tenant=shared_tenant,
        suffix="A101",
        lease_status=LeaseStatus.ACTIVE,
    )

    make_home(
        db,
        owner=owner_b,
        tenant=shared_tenant,
        suffix="B202",
        lease_status=LeaseStatus.ACTIVE,
    )

    make_home(
        db,
        owner=owner_a,
        tenant=old_tenant,
        suffix="AOLD",
        lease_status=LeaseStatus.ENDED,
    )

    response = client.get(
        "/api/owner/tenants/current",
        headers=auth_headers(
            owner_a
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["meta"]["total"] == 1
    assert len(body["items"]) == 1

    item = body["items"][0]

    assert (
        item["tenant"]["id"]
        == shared_tenant.id
    )

    assert (
        item["property_id"]
        == home_a["property"].id
    )

    assert (
        item["unit_id"]
        == home_a["unit"].id
    )


def test_owner_tenant_filters_work(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        email="owner.filters@test.com",
        role=UserRole.OWNER,
        first_name="Filter",
        last_name="Owner",
    )

    tenant = make_user(
        db,
        email="find.me@test.com",
        role=UserRole.TENANT,
        first_name="Find",
        last_name="Me",
    )

    home = make_home(
        db,
        owner=owner,
        tenant=tenant,
        suffix="FILTER1",
        lease_status=LeaseStatus.ACTIVE,
    )

    response = client.get(
        (
            "/api/owner/tenants/current"
            f"?property_id={home['property'].id}"
            "&tenant=find.me"
        ),
        headers=auth_headers(
            owner
        ),
    )

    assert response.status_code == 200
    assert (
        response.json()[
            "meta"
        ]["total"]
        == 1
    )


def test_tenant_home_exposes_only_its_property_owner_contact(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        email="owner.contact@test.com",
        role=UserRole.OWNER,
        first_name="Lina",
        last_name="Owner",
    )

    tenant = make_user(
        db,
        email="tenant.contact@test.com",
        role=UserRole.TENANT,
        first_name="Tenant",
        last_name="Contact",
    )

    other_owner = make_user(
        db,
        email="other.owner@test.com",
        role=UserRole.OWNER,
        first_name="Other",
        last_name="Owner",
    )

    make_home(
        db,
        owner=owner,
        tenant=tenant,
        suffix="CONTACT",
        lease_status=LeaseStatus.ACTIVE,
    )

    other_tenant = make_user(
        db,
        email="other.tenant.contact@test.com",
        role=UserRole.TENANT,
        first_name="Other",
        last_name="Tenant",
    )

    make_home(
        db,
        owner=other_owner,
        tenant=other_tenant,
        suffix="OTHER",
        lease_status=LeaseStatus.ACTIVE,
    )

    response = client.get(
        "/api/tenant/homes",
        headers=auth_headers(
            tenant
        ),
    )

    assert response.status_code == 200

    homes = response.json()

    assert len(homes) == 1

    owner_contact = (
        homes[0]["owner"]
    )

    assert (
        owner_contact["id"]
        == owner.id
    )

    assert (
        owner_contact["email"]
        == "owner.contact@test.com"
    )

    assert (
        owner_contact[
            "phone_number"
        ]
        == "+961 70 111 222"
    )

    assert (
        owner_contact["id"]
        != other_owner.id
    )
