from datetime import date
from decimal import Decimal

from fastapi.testclient import (
    TestClient,
)

from sqlalchemy import (
    func,
    select,
)

from stripe import (
    SignatureVerificationError,
)

from app.api.routes import payments

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
    PaymentStatus,
)

from app.models.property import Property

from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)

from app.models.stripe_event import (
    StripeEvent,
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
    token: str,
) -> dict[str, str]:
    return {
        "Authorization":
            f"Bearer {token}",
    }


def create_user(
    db,
    *,
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


def create_payment_scenario(
    db,
    *,
    suffix: str,
    payment_status=(
        PaymentStatus.PROCESSING
    ),
):
    owner = create_user(
        db,
        email=(
            f"owner.{suffix}@test.com"
        ),
        role=UserRole.OWNER,
    )

    tenant = create_user(
        db,
        email=(
            f"tenant.{suffix}@test.com"
        ),
        role=UserRole.TENANT,
    )

    property_record = Property(
        owner_id=owner.id,
        name=(
            f"Property {suffix}"
        ),
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
        start_date=(
            date(
                2026,
                1,
                1,
            )
        ),
        end_date=None,
        rent_amount=(
            Decimal(
                "1200.00"
            )
        ),
        status=LeaseStatus.ACTIVE,
    )

    db.add(lease)
    db.flush()

    obligation = (
        RentObligation(
            lease_id=lease.id,

            amount=Decimal(
                "1200.00"
            ),

            due_date=date(
                2026,
                10,
                1,
            ),

            status=(
                RentObligationStatus
                .PENDING
            ),
        )
    )

    db.add(obligation)
    db.flush()

    payment = Payment(
        rent_obligation_id=(
            obligation.id
        ),

        tenant_user_id=(
            tenant.id
        ),

        amount=Decimal(
            "1200.00"
        ),

        currency="usd",

        status=payment_status,

        stripe_checkout_session_id=(
            f"cs_test_{suffix}"
        ),
    )

    db.add(payment)
    db.commit()

    db.refresh(owner)
    db.refresh(tenant)
    db.refresh(lease)
    db.refresh(obligation)
    db.refresh(payment)

    return {
        "owner": owner,
        "tenant": tenant,
        "property": (
            property_record
        ),
        "building": building,
        "unit": unit,
        "lease": lease,
        "obligation": obligation,
        "payment": payment,

        "owner_token":
            create_access_token(
                owner.id
            ),

        "tenant_token":
            create_access_token(
                tenant.id
            ),
    }


def test_tenant_sees_own_obligations_and_payments(
    client: TestClient,
    db,
):
    data = (
        create_payment_scenario(
            db,
            suffix="tenant-history",
        )
    )

    headers = auth_headers(
        data["tenant_token"]
    )

    obligation_response = (
        client.get(
            (
                "/api/tenant/homes/"
                f"{data['lease'].id}/"
                "rent-obligations"
            ),
            headers=headers,
        )
    )

    assert (
        obligation_response.status_code
        == 200
    )

    assert (
        obligation_response
        .json()[0]["id"]
        == data["obligation"].id
    )

    payment_response = (
        client.get(
            (
                "/api/tenant/homes/"
                f"{data['lease'].id}/"
                "payments"
            ),
            headers=headers,
        )
    )

    assert (
        payment_response.status_code
        == 200
    )

    history = (
        payment_response.json()
    )

    assert len(history) == 1

    assert (
        history[0]["id"]
        == data["payment"].id
    )

    assert (
        history[0]["status"]
        == "PROCESSING"
    )


def test_cross_tenant_payment_access_fails(
    client: TestClient,
    db,
):
    data = (
        create_payment_scenario(
            db,
            suffix="tenant-a",
        )
    )

    tenant_b = create_user(
        db,
        email=(
            "tenant.b.payments@test.com"
        ),
        role=UserRole.TENANT,
    )

    db.commit()

    token_b = (
        create_access_token(
            tenant_b.id
        )
    )

    response = client.get(
        (
            "/api/tenant/payments/"
            f"{data['payment'].id}"
        ),
        headers=auth_headers(
            token_b
        ),
    )

    assert (
        response.status_code
        == 404
    )

    home_response = client.get(
        (
            "/api/tenant/homes/"
            f"{data['lease'].id}/"
            "payments"
        ),
        headers=auth_headers(
            token_b
        ),
    )

    assert (
        home_response.status_code
        == 404
    )


def test_owner_only_sees_owned_payments(
    client: TestClient,
    db,
):
    data = (
        create_payment_scenario(
            db,
            suffix="owner-a",
        )
    )

    owner_b = create_user(
        db,
        email=(
            "owner.b.payments@test.com"
        ),
        role=UserRole.OWNER,
    )

    db.commit()

    owner_b_token = (
        create_access_token(
            owner_b.id
        )
    )

    owner_a_response = (
        client.get(
            "/api/owner/payments",
            headers=auth_headers(
                data["owner_token"]
            ),
        )
    )

    assert (
        owner_a_response.status_code
        == 200
    )

    assert (
        owner_a_response
        .json()[0]["id"]
        == data["payment"].id
    )

    owner_b_response = (
        client.get(
            "/api/owner/payments",
            headers=auth_headers(
                owner_b_token
            ),
        )
    )

    assert (
        owner_b_response.status_code
        == 200
    )

    assert (
        owner_b_response.json()
        == []
    )

    detail_response = (
        client.get(
            (
                "/api/owner/payments/"
                f"{data['payment'].id}"
            ),
            headers=auth_headers(
                owner_b_token
            ),
        )
    )

    assert (
        detail_response.status_code
        == 404
    )


def test_tenant_cannot_modify_payment_state(
    client: TestClient,
    db,
):
    data = (
        create_payment_scenario(
            db,
            suffix="no-mutation",
        )
    )

    response = client.patch(
        (
            "/api/tenant/payments/"
            f"{data['payment'].id}"
        ),
        headers=auth_headers(
            data["tenant_token"]
        ),
        json={
            "status": "PAID",
        },
    )

    assert (
        response.status_code
        == 405
    )

    db.refresh(
        data["payment"]
    )

    assert (
        data["payment"].status
        == PaymentStatus.PROCESSING
    )


class FakeStripeObject(dict):
    def to_dict(self):
        return dict(self)


class FakeStripeClient:
    def __init__(
        self,
        event,
    ):
        self.event = event

    def construct_event(
        self,
        payload,
        signature,
        secret,
    ):
        return self.event


def test_failed_payment_remains_non_successful(
    client: TestClient,
    db,
    monkeypatch,
):
    data = (
        create_payment_scenario(
            db,
            suffix="failed",
        )
    )

    event = {
        "id":
            "evt_payment_failed",

        "type":
            "payment_intent.payment_failed",

        "data": {
            "object":
                FakeStripeObject({
                    "id":
                        "pi_failed_123",

                    "metadata": {
                        "payment_id":
                            str(
                                data[
                                    "payment"
                                ].id
                            )
                    },
                })
        },
    }

    monkeypatch.setattr(
        payments.settings,
        "stripe_webhook_secret",
        "whsec_test",
    )

    monkeypatch.setattr(
        payments,
        "get_stripe_client",
        lambda:
            FakeStripeClient(
                event
            ),
    )

    response = client.post(
        "/api/stripe/webhook",

        content=b"{}",

        headers={
            "stripe-signature":
                "test-signature"
        },
    )

    assert (
        response.status_code
        == 200
    )

    db.refresh(
        data["payment"]
    )

    db.refresh(
        data["obligation"]
    )

    assert (
        data["payment"].status
        == PaymentStatus.FAILED
    )

    assert (
        data["obligation"].status
        == RentObligationStatus.PENDING
    )


def test_duplicate_webhook_has_one_business_effect(
    client: TestClient,
    db,
    monkeypatch,
):
    data = (
        create_payment_scenario(
            db,
            suffix="duplicate",
        )
    )

    payment = data[
        "payment"
    ]

    event = {
        "id":
            "evt_duplicate_123",

        "type":
            "checkout.session.completed",

        "data": {
            "object":
                FakeStripeObject({
                    "id":
                        payment
                        .stripe_checkout_session_id,

                    "metadata": {
                        "payment_id":
                            str(
                                payment.id
                            )
                    },

                    "amount_total":
                        120000,

                    "currency":
                        "usd",

                    "payment_status":
                        "paid",

                    "payment_intent":
                        "pi_duplicate_123",
                })
        },
    }

    monkeypatch.setattr(
        payments.settings,
        "stripe_webhook_secret",
        "whsec_test",
    )

    monkeypatch.setattr(
        payments,
        "get_stripe_client",
        lambda:
            FakeStripeClient(
                event
            ),
    )

    first = client.post(
        "/api/stripe/webhook",

        content=b"{}",

        headers={
            "stripe-signature":
                "test-signature"
        },
    )

    second = client.post(
        "/api/stripe/webhook",

        content=b"{}",

        headers={
            "stripe-signature":
                "test-signature"
        },
    )

    assert (
        first.status_code
        == 200
    )

    assert (
        first.json()[
            "duplicate"
        ]
        is False
    )

    assert (
        second.status_code
        == 200
    )

    assert (
        second.json()[
            "duplicate"
        ]
        is True
    )

    db.refresh(
        data["payment"]
    )

    db.refresh(
        data["obligation"]
    )

    assert (
        data["payment"].status
        == PaymentStatus.PAID
    )

    assert (
        data["obligation"].status
        == RentObligationStatus.PAID
    )

    event_count = (
        db.scalar(
            select(
                func.count(
                    StripeEvent.id
                )
            ).where(
                StripeEvent
                .stripe_event_id
                == "evt_duplicate_123"
            )
        )
        or 0
    )

    assert event_count == 1


def test_invalid_stripe_signature_fails(
    client: TestClient,
    monkeypatch,
):
    class InvalidSignatureClient:
        def construct_event(
            self,
            payload,
            signature,
            secret,
        ):
            raise (
                SignatureVerificationError(
                    "Invalid signature",
                    signature,
                )
            )

    monkeypatch.setattr(
        payments.settings,
        "stripe_webhook_secret",
        "whsec_test",
    )

    monkeypatch.setattr(
        payments,
        "get_stripe_client",
        lambda:
            InvalidSignatureClient(),
    )

    response = client.post(
        "/api/stripe/webhook",

        content=b"{}",

        headers={
            "stripe-signature":
                "invalid-signature"
        },
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        response.json()[
            "detail"
        ]
        == "Invalid Stripe signature."
    )