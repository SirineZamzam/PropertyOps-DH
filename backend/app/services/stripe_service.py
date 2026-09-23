from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from stripe import StripeClient

from app.core.config import settings
from app.models.payment import Payment
from app.models.rent_obligation import (
    RentObligation,
)
from app.models.user import User


def get_stripe_client() -> StripeClient:
    if not settings.stripe_secret_key:
        raise RuntimeError(
            "Stripe secret key is not configured."
        )

    return StripeClient(
        settings.stripe_secret_key,
        max_network_retries=2,
    )


def amount_to_cents(
    amount: Decimal,
) -> int:
    cents = (
        amount * Decimal("100")
    ).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )

    return int(cents)


def create_checkout_session(
    *,
    payment: Payment,
    obligation: RentObligation,
    tenant: User,
):
    client = get_stripe_client()

    metadata = {
            "flow": "RENT",

            "payment_id": str(
               payment.id
            ),
        "rent_obligation_id": str(
            obligation.id
        ),
        "tenant_user_id": str(
            tenant.id
        ),
    }

    session = (
        client.v1.checkout.sessions.create(
            params={
                "mode": "payment",

                "customer_email":
                    tenant.email,

                "client_reference_id":
                    str(payment.id),

                "line_items": [
                    {
                        "price_data": {
                            "currency":
                                settings.stripe_currency,

                            "product_data": {
                                "name":
                                    (
                                        "PropertyOps "
                                        "Rent Payment"
                                    ),

                                "description":
                                    (
                                        "Rent obligation "
                                        f"#{obligation.id}"
                                    ),
                            },

                            "unit_amount":
                                amount_to_cents(
                                    obligation.amount
                                ),
                        },

                        "quantity": 1,
                    }
                ],

                "metadata":
                    metadata,

                "payment_intent_data": {
                    "metadata":
                        metadata,
                },

                "success_url":
                    (
                        f"{settings.frontend_url}"
                        "/app/rent"
                        "?checkout=success"
                        "&session_id="
                        "{CHECKOUT_SESSION_ID}"
                    ),

                "cancel_url":
                    (
                        f"{settings.frontend_url}"
                        "/app/rent"
                        "?checkout=cancelled"
                    ),
            }
        )
    )

    return session