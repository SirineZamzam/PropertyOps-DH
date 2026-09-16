from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)
from app.models.user import User
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceRead,
    MaintenanceStatusUpdate,
)
from app.services.maintenance import (
    transition_maintenance_status,
)
from app.services.ownership import (
    get_owned_maintenance,
    get_owned_unit,
)


router = APIRouter()


@router.post(
    "/units/{unit_id}/maintenance",
    response_model=MaintenanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance(
    unit_id: int,
    payload: MaintenanceCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Maintenance:
    unit = get_owned_unit(
        db,
        current_owner.id,
        unit_id,
    )

    maintenance = Maintenance(
        unit_id=unit.id,
        created_by_user_id=current_owner.id,
        category=payload.category,
        description=payload.description,
        status=MaintenanceStatus.OPEN,
    )

    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)

    return maintenance


@router.get(
    "/units/{unit_id}/maintenance",
    response_model=list[MaintenanceRead],
)
def list_unit_maintenance(
    unit_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> list[Maintenance]:
    get_owned_unit(
        db,
        current_owner.id,
        unit_id,
    )

    statement = (
        select(Maintenance)
        .where(Maintenance.unit_id == unit_id)
        .order_by(Maintenance.created_at.desc())
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/maintenance/{maintenance_id}",
    response_model=MaintenanceRead,
)
def get_maintenance(
    maintenance_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Maintenance:
    return get_owned_maintenance(
        db,
        current_owner.id,
        maintenance_id,
    )


@router.patch(
    "/maintenance/{maintenance_id}/status",
    response_model=MaintenanceRead,
)
def update_maintenance_status(
    maintenance_id: int,
    payload: MaintenanceStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Maintenance:
    maintenance = get_owned_maintenance(
        db,
        current_owner.id,
        maintenance_id,
    )

    transition_maintenance_status(
        maintenance,
        payload.status,
    )

    db.commit()
    db.refresh(maintenance)

    return maintenance