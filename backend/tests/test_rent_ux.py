from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
from decimal import Decimal

from fastapi.testclient import (
    TestClient,
)

from app.core.security import (
    create_access_token,
)
from app.models.building import Building
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


def create_context(
    db,
):
    owner = User(
        email="owner.rentux@test.com",
        password_hash="test-hash",
        role=UserRole.OWNER,
    )

    tenant = User(
        email="tenant.rentux@test.com",
        password_hash="test-hash",
        role=UserRole.TENANT,
    )

    db.add_all(
        [
            owner,
            tenant,
        ]
    )
    db.flush()

    property_record = Property(
        owner_id=owner.id,
        name="Rent UX Property",
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
        name="Main Building",
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

    obligation = RentObligation(
        lease_id=lease.id,
        amount=Decimal(
            "1000.00"
        ),
        due_date=date(
            2026,
            10,
            1,
        ),
        status=(
            RentObligationStatus.PENDING
        ),
    )

    db.add(obligation)
    db.commit()

    return {
        "owner": owner,
        "tenant": tenant,
        "lease": lease,
        "obligation": obligation,
    }


def test_owner_recent_payment_filter_returns_only_recent_paid(
    client: TestClient,
    db,
):
    data = create_context(db)

    now = datetime.now(
        timezone.utc
    )

    recent_paid = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "1000.00"
        ),
        currency="usd",
        status=PaymentStatus.PAID,
        payment_method=(
            PaymentMethod.CASH
        ),
        paid_at=(
            now
            - timedelta(
                days=2
            )
        ),
    )

    old_paid = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "1000.00"
        ),
        currency="usd",
        status=PaymentStatus.PAID,
        payment_method=(
            PaymentMethod.CASH
        ),
        paid_at=(
            now
            - timedelta(
                days=10
            )
        ),
    )

    recent_failed = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "1000.00"
        ),
        currency="usd",
        status=(
            PaymentStatus.FAILED
        ),
        payment_method=(
            PaymentMethod.STRIPE
        ),
    )

    db.add_all(
        [
            recent_paid,
            old_paid,
            recent_failed,
        ]
    )
    db.commit()

    response = client.get(
        (
            "/api/owner/payments"
            "?limit=20"
            "&payment_status=PAID"
            "&recent_days=7"
        ),
        headers=auth_headers(
            data["owner"]
        ),
    )

    assert (
        response.status_code
        == 200
    )

    ids = {
        item["id"]
        for item
        in response.json()
    }

    assert ids == {
        recent_paid.id
    }


def test_owner_all_payments_still_available(
    client: TestClient,
    db,
):
    data = create_context(db)

    payment = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "1000.00"
        ),
        currency="usd",
        status=(
            PaymentStatus.EXPIRED
        ),
        payment_method=(
            PaymentMethod.STRIPE
        ),
    )

    db.add(payment)
    db.commit()

    response = client.get(
        "/api/owner/payments?limit=100",
        headers=auth_headers(
            data["owner"]
        ),
    )

    assert (
        response.status_code
        == 200
    )

    assert any(
        item["id"]
        == payment.id
        for item
        in response.json()
    )
