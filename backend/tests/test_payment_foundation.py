from decimal import Decimal

from app.models.payment import (
    Payment,
    PaymentStatus,
)

from app.models.stripe_event import (
    StripeEvent,
)


def test_payment_model_values():
    payment = Payment(
        rent_obligation_id=1,
        tenant_user_id=2,
        amount=Decimal("1200.00"),
        currency="usd",
        status=PaymentStatus.PENDING,
    )

    assert (
        payment.rent_obligation_id
        == 1
    )

    assert (
        payment.tenant_user_id
        == 2
    )

    assert (
        payment.amount
        == Decimal("1200.00")
    )

    assert (
        payment.currency
        == "usd"
    )

    assert (
        payment.status
        == PaymentStatus.PENDING
    )


def test_stripe_event_model_values():
    event = StripeEvent(
        stripe_event_id=(
            "evt_test_123"
        ),
        event_type=(
            "checkout.session.completed"
        ),
    )

    assert (
        event.stripe_event_id
        == "evt_test_123"
    )

    assert (
        event.event_type
        == "checkout.session.completed"
    )