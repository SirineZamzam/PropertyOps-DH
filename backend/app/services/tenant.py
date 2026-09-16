from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lease import Lease, LeaseStatus


def get_active_lease_for_tenant(
    db: Session,
    tenant_user_id: int,
) -> Lease:
    statement = select(Lease).where(
        Lease.tenant_user_id == tenant_user_id,
        Lease.status == LeaseStatus.ACTIVE,
    )

    leases = list(
        db.scalars(statement).all()
    )

    if not leases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active lease found.",
        )

    if len(leases) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Multiple active leases found for tenant.",
        )

    return leases[0]