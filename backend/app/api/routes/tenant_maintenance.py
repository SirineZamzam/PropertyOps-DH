from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_tenant
from app.db.session import get_db
from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)
from app.models.user import User
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceRead,
)
from app.services.tenant import (
    get_active_lease_for_tenant,
)


router = APIRouter()


@router.post(
    "/maintenance",
    response_model=MaintenanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant_maintenance(
    payload: MaintenanceCreate,
    db: Annotated[Session, Depends(get_db)],
    current_tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
) -> Maintenance:
    lease = get_active_lease_for_tenant(
        db,
        current_tenant.id,
    )

    maintenance = Maintenance(
        unit_id=lease.unit_id,
        created_by_user_id=current_tenant.id,
        category=payload.category,
        description=payload.description,
        status=MaintenanceStatus.OPEN,
    )

    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)

    return maintenance


@router.get(
    "/maintenance",
    response_model=list[MaintenanceRead],
)
def list_tenant_unit_maintenance(
    db: Annotated[Session, Depends(get_db)],
    current_tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
) -> list[Maintenance]:
    lease = get_active_lease_for_tenant(
        db,
        current_tenant.id,
    )

    statement = (
        select(Maintenance)
        .where(
            Maintenance.unit_id == lease.unit_id
        )
        .order_by(
            Maintenance.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/maintenance/{maintenance_id}",
    response_model=MaintenanceRead,
)
def get_tenant_maintenance(
    maintenance_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
) -> Maintenance:
    lease = get_active_lease_for_tenant(
        db,
        current_tenant.id,
    )

    statement = select(Maintenance).where(
        Maintenance.id == maintenance_id,
        Maintenance.unit_id == lease.unit_id,
    )

    maintenance = db.scalar(statement)

    if maintenance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found.",
        )

    return maintenance