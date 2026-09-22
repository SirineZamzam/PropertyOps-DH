from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import create_access_token
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


def create_user(
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
        phone_number="+961 70 000 000",
    )

    db.add(user)
    db.flush()

    return user


def create_rent_scenario(
    db,
    *,
    suffix: str,
):
    owner = create_user(
        db,
        email=(
            f"owner.{suffix}@test.com"
        ),
        role=UserRole.OWNER,
        first_name="Owner",
        last_name=suffix,
    )

    tenant = create_user(
        db,
        email=(
            f"tenant.{suffix}@test.com"
        ),
        role=UserRole.TENANT,
        first_name="Tenant",
        last_name=suffix,
    )

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
            9,
            1,
        ),
        end_date=date(
            2027,
            9,
            1,
        ),
        rent_amount=Decimal(
            "900.00"
        ),
        status=LeaseStatus.ACTIVE,
    )

    db.add(lease)
    db.flush()

    obligation = RentObligation(
        lease_id=lease.id,
        amount=Decimal(
            "900.00"
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
        "property":
            property_record,
        "building": building,
        "unit": unit,
        "lease": lease,
        "obligation": obligation,
    }


def test_owner_can_record_cash_payment(
    client: TestClient,
    db,
):
    data = create_rent_scenario(
        db,
        suffix="cash",
    )

    response = client.post(
        (
            "/api/owner/"
            "rent-obligations/"
            f"{data['obligation'].id}/"
            "record-cash"
        ),
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "paid_date":
                "2026-09-22",
            "note":
                "Received at office",
        },
    )

    assert (
        response.status_code
        == 201
    )

    body = response.json()

    assert (
        body["status"]
        == "PAID"
    )

    assert (
        body["payment_method"]
        == "CASH"
    )

    assert (
        body["manual_note"]
        == "Received at office"
    )

    db.refresh(
        data["obligation"]
    )

    assert (
        data["obligation"].status
        == RentObligationStatus.PAID
    )

    payment = db.scalar(
        select(Payment).where(
            Payment.rent_obligation_id
            == data["obligation"].id
        )
    )

    assert payment is not None
    assert (
        payment.status
        == PaymentStatus.PAID
    )
    assert (
        payment.payment_method
        == PaymentMethod.CASH
    )


def test_other_owner_cannot_record_cash_payment(
    client: TestClient,
    db,
):
    data = create_rent_scenario(
        db,
        suffix="owner-scope",
    )

    other_owner = create_user(
        db,
        email=(
            "other.owner@test.com"
        ),
        role=UserRole.OWNER,
        first_name="Other",
        last_name="Owner",
    )

    db.commit()

    response = client.post(
        (
            "/api/owner/"
            "rent-obligations/"
            f"{data['obligation'].id}/"
            "record-cash"
        ),
        headers=auth_headers(
            other_owner
        ),
        json={
            "paid_date":
                "2026-09-22",
        },
    )

    assert (
        response.status_code
        == 404
    )


def test_active_stripe_attempt_blocks_cash_payment(
    client: TestClient,
    db,
):
    data = create_rent_scenario(
        db,
        suffix="active-stripe",
    )

    payment = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "900.00"
        ),
        currency="usd",
        status=(
            PaymentStatus.PROCESSING
        ),
        payment_method=(
            PaymentMethod.STRIPE
        ),
        stripe_checkout_session_id=(
            "cs_test_active_cash_block"
        ),
    )

    db.add(payment)
    db.commit()

    response = client.post(
        (
            "/api/owner/"
            "rent-obligations/"
            f"{data['obligation'].id}/"
            "record-cash"
        ),
        headers=auth_headers(
            data["owner"]
        ),
        json={
            "paid_date":
                "2026-09-22",
        },
    )

    assert (
        response.status_code
        == 409
    )


def test_owner_and_tenant_can_download_paid_receipt(
    client: TestClient,
    db,
):
    data = create_rent_scenario(
        db,
        suffix="receipt",
    )

    payment = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "900.00"
        ),
        currency="usd",
        status=(
            PaymentStatus.PAID
        ),
        payment_method=(
            PaymentMethod.CASH
        ),
        manual_note="Receipt test",
    )

    data["obligation"].status = (
        RentObligationStatus.PAID
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    owner_response = client.get(
        (
            "/api/payments/"
            f"{payment.id}/receipt"
        ),
        headers=auth_headers(
            data["owner"]
        ),
    )

    assert (
        owner_response.status_code
        == 200
    )
    assert (
        owner_response.headers[
            "content-type"
        ]
        == "application/pdf"
    )
    assert (
        owner_response.content
        .startswith(b"%PDF")
    )

    tenant_response = client.get(
        (
            "/api/payments/"
            f"{payment.id}/receipt"
        ),
        headers=auth_headers(
            data["tenant"]
        ),
    )

    assert (
        tenant_response.status_code
        == 200
    )
    assert (
        tenant_response.content
        .startswith(b"%PDF")
    )


def test_unrelated_tenant_cannot_download_receipt(
    client: TestClient,
    db,
):
    data = create_rent_scenario(
        db,
        suffix="receipt-scope",
    )

    payment = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "900.00"
        ),
        currency="usd",
        status=(
            PaymentStatus.PAID
        ),
        payment_method=(
            PaymentMethod.CASH
        ),
    )

    data["obligation"].status = (
        RentObligationStatus.PAID
    )

    other_tenant = create_user(
        db,
        email=(
            "other.tenant@test.com"
        ),
        role=UserRole.TENANT,
        first_name="Other",
        last_name="Tenant",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    response = client.get(
        (
            "/api/payments/"
            f"{payment.id}/receipt"
        ),
        headers=auth_headers(
            other_tenant
        ),
    )

    assert (
        response.status_code
        == 404
    )


def test_unpaid_payment_has_no_receipt(
    client: TestClient,
    db,
):
    data = create_rent_scenario(
        db,
        suffix="unpaid-receipt",
    )

    payment = Payment(
        rent_obligation_id=(
            data["obligation"].id
        ),
        tenant_user_id=(
            data["tenant"].id
        ),
        amount=Decimal(
            "900.00"
        ),
        currency="usd",
        status=(
            PaymentStatus.PROCESSING
        ),
        payment_method=(
            PaymentMethod.STRIPE
        ),
        stripe_checkout_session_id=(
            "cs_test_unpaid_receipt"
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    response = client.get(
        (
            "/api/payments/"
            f"{payment.id}/receipt"
        ),
        headers=auth_headers(
            data["tenant"]
        ),
    )

    assert (
        response.status_code
        == 409
    )
