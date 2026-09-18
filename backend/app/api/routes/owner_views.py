import math

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_owner,
)
from app.db.session import get_db

from app.models.building import Building
from app.models.expense import Expense
from app.models.lease import (
    Lease,
    LeaseStatus,
)
from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)
from app.models.property import Property
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
from app.models.unit import Unit
from app.models.user import User

from app.schemas.workflow import (
    OwnerExpenseItem,
    OwnerExpensePage,
    OwnerLeaseItem,
    OwnerLeasePage,
    OwnerMaintenanceItem,
    OwnerMaintenancePage,
    OwnerRentItem,
    OwnerRentPage,
    PageMeta,
)


router = APIRouter()


def make_meta(
    page: int,
    page_size: int,
    total: int,
) -> PageMeta:
    total_pages = (
        math.ceil(
            total / page_size
        )
        if total
        else 0
    )

    return PageMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/owner/leases",
    response_model=OwnerLeasePage,
)
def list_owner_leases(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        8,
        ge=1,
        le=100,
    ),
    property_id: int | None = None,
    building_id: int | None = None,
    unit_id: int | None = None,
    tenant: str | None = None,
    lease_status: LeaseStatus | None = None,
):
    filters = [
        Property.owner_id
        == owner.id
    ]

    if property_id is not None:
        filters.append(
            Property.id
            == property_id
        )

    if building_id is not None:
        filters.append(
            Building.id
            == building_id
        )

    if unit_id is not None:
        filters.append(
            Unit.id
            == unit_id
        )

    if lease_status is not None:
        filters.append(
            Lease.status
            == lease_status
        )

    if tenant:
        pattern = (
            f"%{tenant.strip()}%"
        )

        filters.append(
            or_(
                User.first_name.ilike(
                    pattern
                ),
                User.last_name.ilike(
                    pattern
                ),
                User.email.ilike(
                    pattern
                ),
            )
        )

    count_statement = (
        select(
            func.count(
                Lease.id
            )
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
        .where(*filters)
    )

    total = (
        db.scalar(
            count_statement
        )
        or 0
    )

    statement = (
        select(
            Lease,
            Property,
            Building,
            Unit,
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
            Lease.tenant_user_id
            == User.id,
        )
        .where(*filters)
        .order_by(
            Lease.created_at.desc()
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
    )

    rows = db.execute(
        statement
    ).all()

    items = [
        OwnerLeaseItem(
            id=lease.id,
            status=lease.status,
            start_date=(
                lease.start_date
            ),
            end_date=lease.end_date,
            rent_amount=(
                lease.rent_amount
            ),
            created_at=(
                lease.created_at
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
            tenant=user,
        )
        for (
            lease,
            property_record,
            building,
            unit,
            user,
        ) in rows
    ]

    return OwnerLeasePage(
        items=items,
        meta=make_meta(
            page,
            page_size,
            total,
        ),
    )


@router.get(
    "/owner/maintenance",
    response_model=OwnerMaintenancePage,
)
def list_owner_maintenance(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        8,
        ge=1,
        le=100,
    ),
    property_id: int | None = None,
    building_id: int | None = None,
    unit_id: int | None = None,
    maintenance_status: (
        MaintenanceStatus | None
    ) = None,
    resolved: bool | None = None,
):
    filters = [
        Property.owner_id
        == owner.id
    ]

    if property_id is not None:
        filters.append(
            Property.id
            == property_id
        )

    if building_id is not None:
        filters.append(
            Building.id
            == building_id
        )

    if unit_id is not None:
        filters.append(
            Unit.id
            == unit_id
        )

    if (
        maintenance_status
        is not None
    ):
        filters.append(
            Maintenance.status
            == maintenance_status
        )

    if resolved is True:
        filters.append(
            Maintenance.status
            == MaintenanceStatus.RESOLVED
        )

    if resolved is False:
        filters.append(
            Maintenance.status
            != MaintenanceStatus.RESOLVED
        )

    count_statement = (
        select(
            func.count(
                Maintenance.id
            )
        )
        .join(
            Unit,
            Maintenance.unit_id
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
        .where(*filters)
    )

    total = (
        db.scalar(
            count_statement
        )
        or 0
    )

    statement = (
        select(
            Maintenance,
            Property,
            Building,
            Unit,
            User,
        )
        .join(
            Unit,
            Maintenance.unit_id
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
            Maintenance.created_by_user_id
            == User.id,
        )
        .where(*filters)
        .order_by(
            Maintenance.created_at.desc()
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
    )

    rows = db.execute(
        statement
    ).all()

    items = [
        OwnerMaintenanceItem(
            id=maintenance.id,
            category=(
                maintenance.category
            ),
            description=(
                maintenance.description
            ),
            status=(
                maintenance.status
            ),
            created_at=(
                maintenance.created_at
            ),
            resolved_at=(
                maintenance.resolved_at
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
            creator=creator,
        )
        for (
            maintenance,
            property_record,
            building,
            unit,
            creator,
        ) in rows
    ]

    return OwnerMaintenancePage(
        items=items,
        meta=make_meta(
            page,
            page_size,
            total,
        ),
    )


@router.get(
    "/owner/expenses",
    response_model=OwnerExpensePage,
)
def list_owner_expenses(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        8,
        ge=1,
        le=100,
    ),
    property_id: int | None = None,
    building_id: int | None = None,
    unit_id: int | None = None,
):
    filters = [
        Property.owner_id
        == owner.id
    ]

    if property_id is not None:
        filters.append(
            Property.id
            == property_id
        )

    if building_id is not None:
        filters.append(
            Building.id
            == building_id
        )

    if unit_id is not None:
        filters.append(
            Unit.id
            == unit_id
        )

    count_statement = (
        select(
            func.count(
                Expense.id
            )
        )
        .join(
            Property,
            Expense.property_id
            == Property.id,
        )
        .outerjoin(
            Unit,
            Expense.unit_id
            == Unit.id,
        )
        .outerjoin(
            Building,
            Unit.building_id
            == Building.id,
        )
        .where(*filters)
    )

    total = (
        db.scalar(
            count_statement
        )
        or 0
    )

    statement = (
        select(
            Expense,
            Property,
            Building,
            Unit,
        )
        .join(
            Property,
            Expense.property_id
            == Property.id,
        )
        .outerjoin(
            Unit,
            Expense.unit_id
            == Unit.id,
        )
        .outerjoin(
            Building,
            Unit.building_id
            == Building.id,
        )
        .where(*filters)
        .order_by(
            Expense.expense_date.desc(),
            Expense.created_at.desc(),
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
    )

    rows = db.execute(
        statement
    ).all()

    items = [
        OwnerExpenseItem(
            id=expense.id,
            property_id=(
                property_record.id
            ),
            property_name=(
                property_record.name
            ),
            building_id=(
                building.id
                if building
                else None
            ),
            building_name=(
                building.name
                if building
                else None
            ),
            unit_id=(
                unit.id
                if unit
                else None
            ),
            unit_number=(
                unit.unit_number
                if unit
                else None
            ),
            maintenance_id=(
                expense.maintenance_id
            ),
            amount=expense.amount,
            category=(
                expense.category
            ),
            expense_date=(
                expense.expense_date
            ),
            description=(
                expense.description
            ),
            created_at=(
                expense.created_at
            ),
        )
        for (
            expense,
            property_record,
            building,
            unit,
        ) in rows
    ]

    return OwnerExpensePage(
        items=items,
        meta=make_meta(
            page,
            page_size,
            total,
        ),
    )


@router.get(
    "/owner/rent-obligations",
    response_model=OwnerRentPage,
)
def list_owner_rent(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        8,
        ge=1,
        le=100,
    ),
    property_id: int | None = None,
    building_id: int | None = None,
    unit_id: int | None = None,
    tenant: str | None = None,
    rent_status: (
        RentObligationStatus
        | None
    ) = None,
):
    filters = [
        Property.owner_id
        == owner.id
    ]

    if property_id is not None:
        filters.append(
            Property.id
            == property_id
        )

    if building_id is not None:
        filters.append(
            Building.id
            == building_id
        )

    if unit_id is not None:
        filters.append(
            Unit.id
            == unit_id
        )

    if rent_status is not None:
        filters.append(
            RentObligation.status
            == rent_status
        )

    if tenant:
        pattern = (
            f"%{tenant.strip()}%"
        )

        filters.append(
            or_(
                User.first_name.ilike(
                    pattern
                ),
                User.last_name.ilike(
                    pattern
                ),
                User.email.ilike(
                    pattern
                ),
            )
        )

    count_statement = (
        select(
            func.count(
                RentObligation.id
            )
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
        .where(*filters)
    )

    total = (
        db.scalar(
            count_statement
        )
        or 0
    )

    statement = (
        select(
            RentObligation,
            Lease,
            Property,
            Building,
            Unit,
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
        .where(*filters)
        .order_by(
            RentObligation.due_date.desc()
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
    )

    rows = db.execute(
        statement
    ).all()

    items = [
        OwnerRentItem(
            id=obligation.id,
            amount=obligation.amount,
            due_date=(
                obligation.due_date
            ),
            status=obligation.status,
            created_at=(
                obligation.created_at
            ),
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
            tenant=tenant_user,
        )
        for (
            obligation,
            lease,
            property_record,
            building,
            unit,
            tenant_user,
        ) in rows
    ]

    return OwnerRentPage(
        items=items,
        meta=make_meta(
            page,
            page_size,
            total,
        ),
    )