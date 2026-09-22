from datetime import (
    date,
    datetime,
    timezone,
)
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.models.building import Building
from app.models.expense import Expense
from app.models.lease import (
    Lease,
    LeaseStatus,
)
from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from app.models.property import Property
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
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
    email: str,
    role: UserRole,
):
    user = User(
        email=email,
        password_hash="test-hash",
        role=role,
    )

    db.add(user)
    db.flush()

    return user


def create_owner_context(
    db,
):
    owner = make_user(
        db,
        "finance.owner@test.com",
        UserRole.OWNER,
    )

    tenant = make_user(
        db,
        "finance.tenant@test.com",
        UserRole.TENANT,
    )

    property_record = Property(
        owner_id=owner.id,
        name="Finance Property",
        address="1 Test Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(property_record)
    db.flush()

    building = Building(
        property_id=property_record.id,
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
            "1000.00"
        ),
        status=LeaseStatus.ACTIVE,
    )

    db.add(lease)
    db.flush()

    paid_obligation = RentObligation(
        lease_id=lease.id,
        amount=Decimal(
            "1000.00"
        ),
        due_date=date(
            2026,
            9,
            1,
        ),
        status=(
            RentObligationStatus.PAID
        ),
    )

    pending_obligation = RentObligation(
        lease_id=lease.id,
        amount=Decimal(
            "1000.00"
        ),
        due_date=date(
            2026,
            9,
            20,
        ),
        status=(
            RentObligationStatus.PENDING
        ),
    )

    db.add_all(
        [
            paid_obligation,
            pending_obligation,
        ]
    )
    db.flush()

    payment = Payment(
        rent_obligation_id=(
            paid_obligation.id
        ),
        tenant_user_id=tenant.id,
        amount=Decimal(
            "1000.00"
        ),
        currency="usd",
        status=PaymentStatus.PAID,
        payment_method=(
            PaymentMethod.CASH
        ),
        paid_at=datetime(
            2026,
            9,
            10,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    property_expense = Expense(
        owner_id=owner.id,
        property_id=property_record.id,
        unit_id=None,
        amount=Decimal(
            "200.00"
        ),
        category="Repair",
        expense_date=date(
            2026,
            9,
            11,
        ),
    )

    general_expense = Expense(
        owner_id=owner.id,
        property_id=None,
        unit_id=None,
        amount=Decimal(
            "50.00"
        ),
        category="Software",
        expense_date=date(
            2026,
            9,
            12,
        ),
    )

    db.add_all(
        [
            payment,
            property_expense,
            general_expense,
        ]
    )
    db.commit()

    return {
        "owner": owner,
        "property":
            property_record,
        "unit": unit,
    }


def test_owner_can_create_general_expense(
    client: TestClient,
    db,
):
    owner = make_user(
        db,
        "general.owner@test.com",
        UserRole.OWNER,
    )

    db.commit()

    response = client.post(
        "/api/owner/expenses/general",
        headers=auth_headers(
            owner
        ),
        json={
            "amount": 75.50,
            "category":
                "Software",
            "expense_date":
                "2026-09-22",
            "description":
                "Property management tools",
        },
    )

    assert (
        response.status_code
        == 201
    )

    body = response.json()

    assert (
        body["owner_id"]
        == owner.id
    )

    assert (
        body["property_id"]
        is None
    )

    assert (
        body["unit_id"]
        is None
    )


def test_property_expense_keeps_owner_scope(
    client: TestClient,
    db,
):
    data = create_owner_context(
        db
    )

    response = client.post(
        (
            "/api/properties/"
            f"{data['property'].id}"
            "/expenses"
        ),
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "unit_id": None,
            "amount": 125.00,
            "category":
                "Insurance",
            "expense_date":
                "2026-09-18",
            "description": None,
        },
    )

    assert (
        response.status_code
        == 201
    )

    assert (
        response.json()[
            "owner_id"
        ]
        == data["owner"].id
    )


def test_expense_scopes_are_separated(
    client: TestClient,
    db,
):
    data = create_owner_context(
        db
    )

    property_response = client.get(
        (
            "/api/owner/expenses"
            "?scope=PROPERTY"
        ),
        headers=auth_headers(
            data["owner"]
        ),
    )

    general_response = client.get(
        (
            "/api/owner/expenses"
            "?scope=GENERAL"
        ),
        headers=auth_headers(
            data["owner"]
        ),
    )

    assert (
        property_response.status_code
        == 200
    )

    assert (
        general_response.status_code
        == 200
    )

    assert all(
        item["property_id"]
        is not None
        for item
        in property_response
        .json()["items"]
    )

    assert all(
        item["property_id"]
        is None
        for item
        in general_response
        .json()["items"]
    )


def test_financial_overview_includes_general_expenses(
    client: TestClient,
    db,
):
    data = create_owner_context(
        db
    )

    response = client.get(
        (
            "/api/owner/"
            "financial-overview"
            "?start_date=2026-09-01"
            "&end_date=2026-09-30"
        ),
        headers=auth_headers(
            data["owner"]
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert Decimal(
        body["rent_collected"]
    ) == Decimal(
        "1000.00"
    )

    assert Decimal(
        body["expenses"]
    ) == Decimal(
        "250.00"
    )

    assert Decimal(
        body["net_cash_flow"]
    ) == Decimal(
        "750.00"
    )

    assert Decimal(
        body["outstanding_rent"]
    ) == Decimal(
        "1000.00"
    )

    assert (
        body["bucket"]
        == "DAY"
    )
