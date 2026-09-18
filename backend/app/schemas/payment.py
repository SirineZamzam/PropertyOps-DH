from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.models.payment import (
    PaymentStatus,
)


class PaymentRead(BaseModel):
    id: int

    rent_obligation_id: int
    tenant_user_id: int

    amount: Decimal
    currency: str

    status: PaymentStatus

    stripe_checkout_session_id: (
        str | None
    )

    stripe_payment_intent_id: (
        str | None
    )

    created_at: datetime
    updated_at: datetime

    paid_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )

class CheckoutSessionResponse(BaseModel):
    payment_id: int
    checkout_url: str