from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import (
    create_access_token,
)
from app.models.building import (
    Building,
)
from app.models.lease import (
    LeaseStatus,
)
from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from app.models.property import (
    Property,
)
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
from app.services.lease_rent_schedule import (
    add_calendar_months,
    monthly_due_dates,
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
    *,
    suffix: str,
):
    owner = User(
        email=(
            f"owner.{suffix}@test.com"
        ),
        password_hash="test-hash",
        role=UserRole.OWNER,
        first_name="Owner",
        last_name=suffix,
    )

    tenant = User(
        email=(
            f"tenant.{suffix}@test.com"
        ),
        password_hash="test-hash",
        role=UserRole.TENANT,
        first_name="Tenant",
        last_name=suffix,
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
        name=(
            f"Property {suffix}"
        ),
        address="1 Test Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(
        property_record
    )
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
        status=UnitStatus.VACANT,
    )

    db.add(unit)
    db.commit()

    return {
        "owner": owner,
        "tenant": tenant,
        "property":
            property_record,
        "building": building,
        "unit": unit,
    }


def create_lease(
    client: TestClient,
    data,
    *,
    start_date: str,
    end_date: str | None,
    rent_amount: float = 900.00,
):
    response = client.post(
        (
            "/api/units/"
            f"{data['unit'].id}/leases"
        ),
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "tenant_user_id":
                data["tenant"].id,
            "start_date":
                start_date,
            "end_date":
                end_date,
            "rent_amount":
                rent_amount,
        },
    )

    return response


def lease_obligations(
    db,
    lease_id: int,
):
    return list(
        db.scalars(
            select(
                RentObligation
            )
            .where(
                RentObligation.lease_id
                == lease_id
            )
            .order_by(
                RentObligation.due_date
            )
        ).all()
    )


def test_calendar_month_math_handles_month_end():
    assert (
        add_calendar_months(
            date(
                2027,
                1,
                31,
            ),
            1,
        )
        == date(
            2027,
            2,
            28,
        )
    )

    assert (
        add_calendar_months(
            date(
                2028,
                1,
                31,
            ),
            1,
        )
        == date(
            2028,
            2,
            29,
        )
    )

    assert monthly_due_dates(
        date(
            2027,
            1,
            31,
        ),
        date(
            2027,
            4,
            30,
        ),
    ) == [
        date(
            2027,
            1,
            31,
        ),
        date(
            2027,
            2,
            28,
        ),
        date(
            2027,
            3,
            31,
        ),
    ]


def test_create_lease_generates_monthly_obligations(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="generate",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-31",
        end_date="2099-04-30",
    )

    assert (
        response.status_code
        == 201
    )

    lease_id = (
        response.json()["id"]
    )

    obligations = (
        lease_obligations(
            db,
            lease_id,
        )
    )

    assert [
        item.due_date
        for item
        in obligations
    ] == [
        date(
            2099,
            1,
            31,
        ),
        date(
            2099,
            2,
            28,
        ),
        date(
            2099,
            3,
            31,
        ),
    ]

    assert all(
        item.amount
        == Decimal(
            "900.00"
        )
        for item
        in obligations
    )

    assert all(
        item.status
        == RentObligationStatus.PENDING
        for item
        in obligations
    )


def test_invalid_non_monthly_term_is_rejected(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="invalid-term",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-31",
        end_date="2099-04-29",
    )

    assert (
        response.status_code
        == 422
    )

    assert (
        "calendar-month"
        in response.json()[
            "detail"
        ]
    )


def test_rent_change_updates_only_scheduled_future_obligations(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="rent-change",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-31",
        end_date="2099-04-30",
    )

    assert (
        response.status_code
        == 201
    )

    lease_id = (
        response.json()["id"]
    )

    obligations = (
        lease_obligations(
            db,
            lease_id,
        )
    )

    # Preserve a paid historical business record.
    obligations[0].status = (
        RentObligationStatus.PAID
    )

    # Manual/custom obligation remains supported
    # and should not be rewritten by monthly schedule sync.
    manual = RentObligation(
        lease_id=lease_id,
        amount=Decimal(
            "777.00"
        ),
        due_date=date(
            2099,
            3,
            15,
        ),
        status=(
            RentObligationStatus.PENDING
        ),
    )

    db.add(manual)
    db.commit()

    update = client.patch(
        f"/api/leases/{lease_id}",
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "rent_amount":
                1100.00,
            "end_date":
                "2099-05-31",
        },
    )

    assert (
        update.status_code
        == 200
    )

    obligations = (
        lease_obligations(
            db,
            lease_id,
        )
    )

    by_date = {
        item.due_date:
            item
        for item
        in obligations
    }

    assert (
        by_date[
            date(
                2099,
                1,
                31,
            )
        ].amount
        == Decimal(
            "900.00"
        )
    )

    assert (
        by_date[
            date(
                2099,
                1,
                31,
            )
        ].status
        == RentObligationStatus.PAID
    )

    for scheduled_date in [
        date(
            2099,
            2,
            28,
        ),
        date(
            2099,
            3,
            31,
        ),
        date(
            2099,
            4,
            30,
        ),
    ]:
        assert (
            by_date[
                scheduled_date
            ].amount
            == Decimal(
                "1100.00"
            )
        )

        assert (
            by_date[
                scheduled_date
            ].status
            == RentObligationStatus.PENDING
        )

    assert (
        by_date[
            date(
                2099,
                3,
                15,
            )
        ].amount
        == Decimal(
            "777.00"
        )
    )


def test_shortening_term_cancels_future_obligations(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="shorten",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-31",
        end_date="2099-05-31",
    )

    lease_id = (
        response.json()["id"]
    )

    update = client.patch(
        f"/api/leases/{lease_id}",
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "end_date":
                "2099-03-31",
        },
    )

    assert (
        update.status_code
        == 200
    )

    obligations = (
        lease_obligations(
            db,
            lease_id,
        )
    )

    by_date = {
        item.due_date:
            item.status
        for item
        in obligations
    }

    assert (
        by_date[
            date(
                2099,
                1,
                31,
            )
        ]
        == RentObligationStatus.PENDING
    )

    assert (
        by_date[
            date(
                2099,
                2,
                28,
            )
        ]
        == RentObligationStatus.PENDING
    )

    assert (
        by_date[
            date(
                2099,
                3,
                31,
            )
        ]
        == RentObligationStatus.CANCELED
    )

    assert (
        by_date[
            date(
                2099,
                4,
                30,
            )
        ]
        == RentObligationStatus.CANCELED
    )


def test_manual_obligation_still_supported(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="manual",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-31",
        end_date="2099-04-30",
    )

    lease_id = (
        response.json()["id"]
    )

    manual = client.post(
        (
            f"/api/leases/{lease_id}"
            "/obligations"
        ),
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "amount": 250.00,
            "due_date":
                "2099-03-15",
        },
    )

    assert (
        manual.status_code
        == 201
    )

    assert (
        manual.json()[
            "amount"
        ]
        == "250.00"
    )


def test_lease_start_date_cannot_be_changed_after_creation(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="start-fixed",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-31",
        end_date="2099-04-30",
    )

    lease_id = (
        response.json()["id"]
    )

    update = client.patch(
        f"/api/leases/{lease_id}",
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "start_date":
                "2099-02-28",
        },
    )

    assert (
        update.status_code
        == 409
    )


def test_end_lease_cancels_future_obligations_and_expires_attempts(
    client: TestClient,
    db,
):
    data = create_context(
        db,
        suffix="end-lease",
    )

    response = create_lease(
        client,
        data,
        start_date="2099-01-01",
        end_date="2100-01-01",
    )

    assert (
        response.status_code
        == 201
    )

    lease_id = (
        response.json()["id"]
    )

    obligation = (
        lease_obligations(
            db,
            lease_id,
        )[0]
    )

    payment = Payment(
        rent_obligation_id=(
            obligation.id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=(
            obligation.amount
        ),
        currency="usd",
        status=(
            PaymentStatus.PROCESSING
        ),
        payment_method=(
            PaymentMethod.STRIPE
        ),
        stripe_checkout_session_id=(
            "cs_test_end_lease"
        ),
    )

    db.add(payment)
    db.commit()

    end_response = client.post(
        f"/api/leases/{lease_id}/end",
        headers=auth_headers(
            data["owner"]
        ),
    )

    assert (
        end_response.status_code
        == 200
    )

    assert (
        end_response.json()[
            "status"
        ]
        == LeaseStatus.ENDED.value
    )

    db.refresh(
        obligation
    )
    db.refresh(
        payment
    )

    assert (
        obligation.status
        == RentObligationStatus.CANCELED
    )

    assert (
        payment.status
        == PaymentStatus.EXPIRED
    )
