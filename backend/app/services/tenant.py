from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lease import (
    Lease,
    LeaseStatus,
)


def get_active_leases_for_tenant(
    db: Session,
    tenant_user_id: int,
) -> list[Lease]:
    statement = (
        select(Lease)
        .where(
            Lease.tenant_user_id
            == tenant_user_id,
            Lease.status
            == LeaseStatus.ACTIVE,
        )
        .order_by(
            Lease.start_date.asc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_active_lease_for_tenant(
    db: Session,
    tenant_user_id: int,
) -> Lease:
    leases = get_active_leases_for_tenant(
        db,
        tenant_user_id,
    )

    if not leases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active lease found.",
        )

    if len(leases) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Multiple active leases found. "
                "Select the home you want to use."
            ),
        )

    return leases[0]