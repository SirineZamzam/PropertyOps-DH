import math
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_admin,
)
from app.db.session import get_db
from app.models.building import Building
from app.models.lease import (
    Lease,
    LeaseStatus,
)
from app.models.property import Property
from app.models.unit import Unit
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.admin import (
    AdminOverviewRead,
    AdminOwnerItem,
    AdminOwnerPage,
    AdminOwnerStatusUpdate,
    AdminPageMeta,
)


router = APIRouter()


def make_meta(
    page: int,
    page_size: int,
    total: int,
) -> AdminPageMeta:
    total_pages = (
        math.ceil(
            total / page_size
        )
        if total
        else 0
    )

    return AdminPageMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def owner_counts():
    property_count = (
        select(
            func.count(
                Property.id
            )
        )
        .where(
            Property.owner_id
            == User.id
        )
        .correlate(User)
        .scalar_subquery()
    )

    building_count = (
        select(
            func.count(
                Building.id
            )
        )
        .join(
            Property,
            Building.property_id
            == Property.id,
        )
        .where(
            Property.owner_id
            == User.id
        )
        .correlate(User)
        .scalar_subquery()
    )

    unit_count = (
        select(
            func.count(
                Unit.id
            )
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
        .where(
            Property.owner_id
            == User.id
        )
        .correlate(User)
        .scalar_subquery()
    )

    active_lease_count = (
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
        .where(
            Property.owner_id
            == User.id,
            Lease.status
            == LeaseStatus.ACTIVE,
        )
        .correlate(User)
        .scalar_subquery()
    )

    return (
        property_count,
        building_count,
        unit_count,
        active_lease_count,
    )


@router.get(
    "/admin/overview",
    response_model=(
        AdminOverviewRead
    ),
)
def admin_overview(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    total_owners = (
        db.scalar(
            select(
                func.count(
                    User.id
                )
            ).where(
                User.role
                == UserRole.OWNER
            )
        )
        or 0
    )

    active_owners = (
        db.scalar(
            select(
                func.count(
                    User.id
                )
            ).where(
                User.role
                == UserRole.OWNER,
                User.is_active
                .is_(True),
            )
        )
        or 0
    )

    inactive_owners = (
        total_owners
        - active_owners
    )

    total_properties = (
        db.scalar(
            select(
                func.count(
                    Property.id
                )
            )
        )
        or 0
    )

    total_units = (
        db.scalar(
            select(
                func.count(
                    Unit.id
                )
            )
        )
        or 0
    )

    return AdminOverviewRead(
        total_owners=(
            total_owners
        ),
        active_owners=(
            active_owners
        ),
        inactive_owners=(
            inactive_owners
        ),
        total_properties=(
            total_properties
        ),
        total_units=(
            total_units
        ),
    )


@router.get(
    "/admin/owners",
    response_model=AdminOwnerPage,
)
def list_admin_owners(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    search: str | None = None,
    active: bool | None = None,
):
    filters = [
        User.role
        == UserRole.OWNER
    ]

    if search:
        pattern = (
            f"%{search.strip()}%"
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
                User.phone_number.ilike(
                    pattern
                ),
            )
        )

    if active is not None:
        filters.append(
            User.is_active
            .is_(active)
        )

    total = (
        db.scalar(
            select(
                func.count(
                    User.id
                )
            ).where(
                *filters
            )
        )
        or 0
    )

    (
        property_count,
        building_count,
        unit_count,
        active_lease_count,
    ) = owner_counts()

    statement = (
        select(
            User,
            property_count.label(
                "property_count"
            ),
            building_count.label(
                "building_count"
            ),
            unit_count.label(
                "unit_count"
            ),
            active_lease_count.label(
                "active_lease_count"
            ),
        )
        .where(
            *filters
        )
        .order_by(
            User.created_at.desc(),
            User.id.desc(),
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(
            page_size
        )
    )

    rows = db.execute(
        statement
    ).all()

    items = [
        AdminOwnerItem(
            id=owner.id,
            first_name=(
                owner.first_name
            ),
            last_name=(
                owner.last_name
            ),
            phone_number=(
                owner.phone_number
            ),
            email=owner.email,
            is_active=(
                owner.is_active
            ),
            created_at=(
                owner.created_at
            ),
            property_count=(
                property_total
                or 0
            ),
            building_count=(
                building_total
                or 0
            ),
            unit_count=(
                unit_total
                or 0
            ),
            active_lease_count=(
                lease_total
                or 0
            ),
        )
        for (
            owner,
            property_total,
            building_total,
            unit_total,
            lease_total,
        ) in rows
    ]

    return AdminOwnerPage(
        items=items,
        meta=make_meta(
            page,
            page_size,
            total,
        ),
    )


@router.patch(
    "/admin/owners/{owner_id}/status",
    response_model=AdminOwnerItem,
)
def update_owner_status(
    owner_id: int,
    payload: (
        AdminOwnerStatusUpdate
    ),
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    owner = db.scalar(
        select(User).where(
            User.id
            == owner_id,
            User.role
            == UserRole.OWNER,
        )
    )

    if owner is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Owner account not found."
            ),
        )

    owner.is_active = (
        payload.is_active
    )

    db.commit()
    db.refresh(owner)

    (
        property_count,
        building_count,
        unit_count,
        active_lease_count,
    ) = owner_counts()

    counts = db.execute(
        select(
            property_count,
            building_count,
            unit_count,
            active_lease_count,
        ).where(
            User.id
            == owner.id
        )
    ).one()

    return AdminOwnerItem(
        id=owner.id,
        first_name=(
            owner.first_name
        ),
        last_name=(
            owner.last_name
        ),
        phone_number=(
            owner.phone_number
        ),
        email=owner.email,
        is_active=owner.is_active,
        created_at=(
            owner.created_at
        ),
        property_count=(
            counts[0]
            or 0
        ),
        building_count=(
            counts[1]
            or 0
        ),
        unit_count=(
            counts[2]
            or 0
        ),
        active_lease_count=(
            counts[3]
            or 0
        ),
    )
