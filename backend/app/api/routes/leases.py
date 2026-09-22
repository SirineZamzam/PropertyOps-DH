from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_owner,
)
from app.db.session import get_db
from app.models.lease import (
    Lease,
    LeaseStatus,
)
from app.models.unit import UnitStatus
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.lease import (
    LeaseCreate,
    LeaseRead,
)
from app.services.lease_rent_schedule import (
    cancel_future_obligations,
    generate_initial_rent_schedule,
    validate_lease_term,
)
from app.services.ownership import (
    get_owned_lease,
    get_owned_unit,
)


router = APIRouter()


@router.post(
    "/units/{unit_id}/leases",
    response_model=LeaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_lease(
    unit_id: int,
    payload: LeaseCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Lease:
    unit = get_owned_unit(
        db,
        current_owner.id,
        unit_id,
    )

    tenant = db.get(
        User,
        payload.tenant_user_id,
    )

    if (
        tenant is None
        or tenant.role
        != UserRole.TENANT
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "A valid tenant "
                "account is required."
            ),
        )

    try:
        validate_lease_term(
            payload.start_date,
            payload.end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc

    lease = Lease(
        unit_id=unit.id,
        tenant_user_id=tenant.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        rent_amount=payload.rent_amount,
        status=LeaseStatus.ACTIVE,
    )

    try:
        db.add(lease)

        # We need the lease ID before generating
        # its monthly rent obligations.
        db.flush()

        generate_initial_rent_schedule(
            db,
            lease,
        )

        if (
            unit.status
            != UnitStatus.UNAVAILABLE
        ):
            unit.status = (
                UnitStatus.OCCUPIED
            )

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This unit already has "
                "an active lease."
            ),
        )

    db.refresh(lease)

    return lease


@router.get(
    "/units/{unit_id}/leases",
    response_model=list[
        LeaseRead
    ],
)
def list_unit_leases(
    unit_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> list[Lease]:
    get_owned_unit(
        db,
        current_owner.id,
        unit_id,
    )

    statement = (
        select(Lease)
        .where(
            Lease.unit_id
            == unit_id
        )
        .order_by(
            Lease.start_date.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


@router.post(
    "/leases/{lease_id}/end",
    response_model=LeaseRead,
)
def end_lease(
    lease_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Lease:
    lease = get_owned_lease(
        db,
        current_owner.id,
        lease_id,
    )

    unit = get_owned_unit(
        db,
        current_owner.id,
        lease.unit_id,
    )

    if (
        lease.status
        == LeaseStatus.ENDED
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Lease is already ended."
            ),
        )

    today = date.today()

    # If a future lease is ended before it starts,
    # use its start date as the effective boundary.
    effective_end = max(
        today,
        lease.start_date,
    )

    lease.status = (
        LeaseStatus.ENDED
    )

    lease.end_date = (
        effective_end
    )

    cancel_future_obligations(
        db,
        lease,
        cutoff=effective_end,
    )

    if (
        unit.status
        != UnitStatus.UNAVAILABLE
    ):
        unit.status = (
            UnitStatus.VACANT
        )

    db.commit()
    db.refresh(lease)

    return lease
