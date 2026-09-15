from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.lease import LeaseStatus
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
from app.models.user import User
from app.schemas.rent_obligation import (
    RentObligationCreate,
    RentObligationRead,
)
from app.services.ownership import get_owned_lease


router = APIRouter()


@router.post(
    "/leases/{lease_id}/obligations",
    response_model=RentObligationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_rent_obligation(
    lease_id: int,
    payload: RentObligationCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> RentObligation:
    lease = get_owned_lease(
        db,
        current_owner.id,
        lease_id,
    )

    if lease.status != LeaseStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rent obligations can only be created for an active lease.",
        )

    if payload.due_date < lease.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date cannot be before the lease start date.",
        )

    if (
        lease.end_date is not None
        and payload.due_date > lease.end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date cannot be after the lease end date.",
        )

    obligation = RentObligation(
        lease_id=lease.id,
        amount=payload.amount,
        due_date=payload.due_date,
        status=RentObligationStatus.PENDING,
    )

    db.add(obligation)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A rent obligation already exists for this lease and due date.",
        )

    db.refresh(obligation)

    return obligation


@router.get(
    "/leases/{lease_id}/obligations",
    response_model=list[RentObligationRead],
)
def list_rent_obligations(
    lease_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> list[RentObligation]:
    get_owned_lease(
        db,
        current_owner.id,
        lease_id,
    )

    statement = (
        select(RentObligation)
        .where(RentObligation.lease_id == lease_id)
        .order_by(RentObligation.due_date.desc())
    )

    return list(db.scalars(statement).all())