from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_tenant,
)
from app.db.session import get_db

from app.models.building import Building
from app.models.lease import (
    Lease,
    LeaseStatus,
)
from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)
from app.models.property import Property
from app.models.unit import Unit
from app.models.user import User

from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceRead,
)
from app.schemas.workflow import (
    TenantHomeItem,
)


router = APIRouter()


def get_tenant_active_lease(
    db: Session,
    tenant_id: int,
    lease_id: int,
) -> Lease:
    lease = db.scalar(
        select(Lease).where(
            Lease.id == lease_id,
            Lease.tenant_user_id
            == tenant_id,
            Lease.status
            == LeaseStatus.ACTIVE,
        )
    )

    if lease is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Active lease not found."
            ),
        )

    return lease


@router.get(
    "/tenant/homes",
    response_model=list[TenantHomeItem],
)
def list_tenant_homes(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
):
    statement = (
        select(
            Lease,
            Unit,
            Building,
            Property,
            User,
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
            Property.owner_id
            == User.id,
        )
        .where(
            Lease.tenant_user_id
            == tenant.id,
            Lease.status
            == LeaseStatus.ACTIVE,
        )
        .order_by(
            Lease.start_date.asc()
        )
    )

    rows = db.execute(
        statement
    ).all()

    return [
        TenantHomeItem(
            lease_id=lease.id,
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
            rent_amount=(
                lease.rent_amount
            ),
            start_date=(
                lease.start_date
            ),
            end_date=(
                lease.end_date
            ),
            owner=owner_user,
        )
        for (
            lease,
            unit,
            building,
            property_record,
            owner_user,
        ) in rows
    ]


@router.get(
    "/tenant/homes/{lease_id}/maintenance",
    response_model=list[MaintenanceRead],
)
def list_home_maintenance(
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
    lease = get_tenant_active_lease(
        db,
        tenant.id,
        lease_id,
    )

    statement = (
        select(Maintenance)
        .where(
            Maintenance.unit_id
            == lease.unit_id
        )
        .order_by(
            Maintenance.created_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


@router.post(
    "/tenant/homes/{lease_id}/maintenance",
    response_model=MaintenanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_home_maintenance(
    lease_id: int,
    payload: MaintenanceCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
):
    lease = get_tenant_active_lease(
        db,
        tenant.id,
        lease_id,
    )

    maintenance = Maintenance(
        unit_id=lease.unit_id,
        created_by_user_id=(
            tenant.id
        ),
        category=payload.category,
        description=(
            payload.description
        ),
        status=(
            MaintenanceStatus.OPEN
        ),
    )

    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)

    return maintenance