from datetime import (
    date,
    datetime,
    time,
    timezone,
)
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    require_owner,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.building import Building
from app.models.lease import Lease
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
from app.models.unit import Unit
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.payment import (
    ManualPaymentCreate,
    OwnerPaymentHistoryRead,
)
from app.services.payment_receipt import (
    build_payment_receipt,
)


router = APIRouter()


def owned_obligation_context(
    db: Session,
    *,
    owner_id: int,
    obligation_id: int,
):
    return db.execute(
        select(
            RentObligation,
            Lease,
            Unit,
            Building,
            Property,
            User,
        )
        .join(
            Lease,
            RentObligation.lease_id
            == Lease.id,
        )
        .join(
            Unit,
            Lease.unit_id
            == Unit.id,
        )
        .join(
            Building,
            Unit.building_id
            == Building.id,
        )
        .join(
            Property,
            Building.property_id
            == Property.id,
        )
        .join(
            User,
            Lease.tenant_user_id
            == User.id,
        )
        .where(
            RentObligation.id
            == obligation_id,
            Property.owner_id
            == owner_id,
        )
    ).one_or_none()


def payment_context(
    db: Session,
    payment_id: int,
):
    return db.execute(
        select(
            Payment,
            RentObligation,
            Lease,
            Unit,
            Building,
            Property,
            User,
        )
        .join(
            RentObligation,
            Payment.rent_obligation_id
            == RentObligation.id,
        )
        .join(
            Lease,
            RentObligation.lease_id
            == Lease.id,
        )
        .join(
            Unit,
            Lease.unit_id
            == Unit.id,
        )
        .join(
            Building,
            Unit.building_id
            == Building.id,
        )
        .join(
            Property,
            Building.property_id
            == Property.id,
        )
        .join(
            User,
            Lease.tenant_user_id
            == User.id,
        )
        .where(
            Payment.id
            == payment_id,
        )
    ).one_or_none()


@router.post(
    "/owner/rent-obligations/"
    "{obligation_id}/record-cash",
    response_model=(
        OwnerPaymentHistoryRead
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def record_cash_payment(
    obligation_id: int,
    payload: ManualPaymentCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    row = owned_obligation_context(
        db,
        owner_id=owner.id,
        obligation_id=obligation_id,
    )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Rent obligation "
                "not found."
            ),
        )

    (
        obligation,
        lease,
        unit,
        building,
        property_record,
        tenant,
    ) = row

    if (
        obligation.status
        != RentObligationStatus.PENDING
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Only pending rent "
                "obligations can be "
                "recorded as paid."
            ),
        )

    if (
        payload.paid_date
        and payload.paid_date
        > date.today()
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Paid date cannot be "
                "in the future."
            ),
        )

    active_stripe_payment = db.scalar(
        select(
            Payment
        )
        .where(
            Payment.rent_obligation_id
            == obligation.id,
            Payment.payment_method
            == PaymentMethod.STRIPE,
            Payment.status.in_(
                [
                    PaymentStatus.PENDING,
                    PaymentStatus.PROCESSING,
                ]
            ),
        )
        .order_by(
            Payment.created_at.desc()
        )
    )

    if active_stripe_payment:
        raise HTTPException(
            status_code=409,
            detail=(
                "This obligation has an "
                "active Stripe payment "
                "attempt. Let that attempt "
                "finish or expire before "
                "recording a cash payment."
            ),
        )

    if payload.paid_date:
        paid_at = datetime.combine(
            payload.paid_date,
            time.min,
            tzinfo=timezone.utc,
        )
    else:
        paid_at = datetime.now(
            timezone.utc
        )

    note = (
        payload.note.strip()
        if payload.note
        else None
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
            PaymentStatus.PAID
        ),
        payment_method=(
            PaymentMethod.CASH
        ),
        manual_note=(
            note or None
        ),
        paid_at=paid_at,
    )

    obligation.status = (
        RentObligationStatus.PAID
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.refresh(obligation)

    return OwnerPaymentHistoryRead(
        id=payment.id,
        rent_obligation_id=(
            payment.rent_obligation_id
        ),
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        payment_method=(
            payment.payment_method
        ),
        manual_note=(
            payment.manual_note
        ),
        due_date=(
            obligation.due_date
        ),
        created_at=(
            payment.created_at
        ),
        paid_at=(
            payment.paid_at
        ),
        tenant_user_id=(
            tenant.id
        ),
        tenant_email=(
            tenant.email
        ),
        tenant_first_name=(
            tenant.first_name
        ),
        tenant_last_name=(
            tenant.last_name
        ),
        property_id=(
            property_record.id
        ),
        property_name=(
            property_record.name
        ),
        building_id=(
            building.id
        ),
        building_name=(
            building.name
        ),
        unit_id=unit.id,
        unit_number=(
            unit.unit_number
        ),
    )


@router.get(
    "/payments/{payment_id}/receipt",
)
def download_payment_receipt(
    payment_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    row = payment_context(
        db,
        payment_id,
    )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    (
        payment,
        obligation,
        lease,
        unit,
        building,
        property_record,
        tenant,
    ) = row

    allowed = False

    if (
        current_user.role
        == UserRole.OWNER
    ):
        allowed = (
            property_record.owner_id
            == current_user.id
        )

    elif (
        current_user.role
        == UserRole.TENANT
    ):
        allowed = (
            lease.tenant_user_id
            == current_user.id
            and payment.tenant_user_id
            == current_user.id
        )

    if not allowed:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    if (
        payment.status
        != PaymentStatus.PAID
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "A receipt is only "
                "available for a paid "
                "payment."
            ),
        )

    owner = db.get(
        User,
        property_record.owner_id,
    )

    if owner is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Property owner could "
                "not be loaded."
            ),
        )

    pdf = build_payment_receipt(
        payment=payment,
        obligation=obligation,
        tenant=tenant,
        owner=owner,
        property_record=(
            property_record
        ),
        building=building,
        unit=unit,
    )

    filename = (
        "propertyops-receipt-"
        f"{payment.id}.pdf"
    )

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                (
                    "attachment; "
                    f'filename="{filename}"'
                )
        },
    )
