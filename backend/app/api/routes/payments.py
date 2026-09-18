from datetime import date
import stripe
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_tenant,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.lease import Lease
from app.models.payment import (
    Payment,
    PaymentStatus,
)
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
from app.models.user import User
from app.schemas.payment import (
    CheckoutSessionResponse,
)
from app.services.stripe_service import (
    create_checkout_session,
)

router = APIRouter()


class TenantRentObligationRead(
    BaseModel
):
    id: int
    lease_id: int
    amount: float
    due_date: date
    status: RentObligationStatus

    model_config = {
        "from_attributes": True
    }


def get_tenant_obligation(
    db: Session,
    tenant_id: int,
    obligation_id: int,
) -> RentObligation:
    obligation = db.scalar(
        select(
            RentObligation
        )
        .join(
            Lease,
            RentObligation.lease_id
            == Lease.id,
        )
        .where(
            RentObligation.id
            == obligation_id,

            Lease.tenant_user_id
            == tenant_id,
        )
    )

    if obligation is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Rent obligation not found."
            ),
        )

    return obligation


@router.get(
    "/tenant/homes/{lease_id}/"
    "rent-obligations",

    response_model=list[
        TenantRentObligationRead
    ],
)
def list_tenant_rent_obligations(
    lease_id: int,

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
):
    lease = db.scalar(
        select(Lease).where(
            Lease.id == lease_id,

            Lease.tenant_user_id
            == tenant.id,
        )
    )

    if lease is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Lease not found."
            ),
        )

    obligations = db.scalars(
        select(
            RentObligation
        )
        .where(
            RentObligation.lease_id
            == lease.id
        )
        .order_by(
            RentObligation
            .due_date.desc()
        )
    ).all()

    return list(obligations)


@router.post(
    "/tenant/rent-obligations/"
    "{obligation_id}/checkout",

    response_model=(
        CheckoutSessionResponse
    ),
)
def create_rent_checkout(
    obligation_id: int,

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
):
    obligation = (
        get_tenant_obligation(
            db,
            tenant.id,
            obligation_id,
        )
    )

    if (
        obligation.status
        != RentObligationStatus.PENDING
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only pending rent "
                "obligations can be paid."
            ),
        )

    payment = Payment(
        rent_obligation_id=(
            obligation.id
        ),

        tenant_user_id=(
            tenant.id
        ),

        amount=(
            obligation.amount
        ),

        currency=(
            settings.stripe_currency
        ),

        status=(
            PaymentStatus.PENDING
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    try:
        session = (
            create_checkout_session(
                payment=payment,
                obligation=obligation,
                tenant=tenant,
            )
        )

    except Exception:
        payment.status = (
            PaymentStatus.FAILED
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to start Stripe "
                "Checkout. Please try again."
            ),
        )

    if not session.url:
        payment.status = (
            PaymentStatus.FAILED
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Stripe did not return "
                "a checkout URL."
            ),
        )

    payment.stripe_checkout_session_id = (
        session.id
    )

    payment.status = (
        PaymentStatus.PROCESSING
    )

    db.commit()

    return CheckoutSessionResponse(
        payment_id=payment.id,
        checkout_url=session.url,
    )