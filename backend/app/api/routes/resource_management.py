from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import (
    IntegrityError,
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
from app.models.unit import (
    Unit,
    UnitStatus,
)
from app.models.user import User

from app.schemas.workflow import (
    BuildingUpdate,
    BuildingView,
    ExpenseUpdate,
    LeaseCore,
    LeaseUpdate,
    MaintenanceUpdate,
    PropertyUpdate,
    PropertyView,
    RentObligationUpdate,
    UnitOccupancyView,
    UnitUpdate,
    UnitView,
)

from app.services.ownership import (
    get_owned_building,
    get_owned_lease,
    get_owned_maintenance,
    get_owned_property,
    get_owned_unit,
)


router = APIRouter()


def get_owned_expense(
    db: Session,
    owner_id: int,
    expense_id: int,
) -> Expense:
    statement = (
        select(Expense)
        .join(
            Property,
            Expense.property_id
            == Property.id,
        )
        .where(
            Expense.id == expense_id,
            Property.owner_id
            == owner_id,
        )
    )

    expense = db.scalar(statement)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    return expense


def get_owned_obligation(
    db: Session,
    owner_id: int,
    obligation_id: int,
) -> RentObligation:
    statement = (
        select(RentObligation)
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
        .where(
            RentObligation.id
            == obligation_id,
            Property.owner_id
            == owner_id,
        )
    )

    obligation = db.scalar(
        statement
    )

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Rent obligation not found."
            ),
        )

    return obligation


# ---------------------------------
# PROPERTIES
# ---------------------------------

@router.patch(
    "/properties/{property_id}",
    response_model=PropertyView,
)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    property_record = (
        get_owned_property(
            db,
            owner.id,
            property_id,
        )
    )

    for (
        field,
        value,
    ) in payload.model_dump(
        exclude_unset=True,
    ).items():
        setattr(
            property_record,
            field,
            value,
        )

    db.commit()
    db.refresh(
        property_record
    )

    return property_record


@router.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_property(
    property_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    property_record = (
        get_owned_property(
            db,
            owner.id,
            property_id,
        )
    )

    building_count = (
        db.scalar(
            select(
                func.count(
                    Building.id
                )
            ).where(
                Building.property_id
                == property_id
            )
        )
        or 0
    )

    if building_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Delete the property's "
                "buildings first."
            ),
        )

    db.delete(property_record)
    db.commit()

    return None


# ---------------------------------
# BUILDINGS
# ---------------------------------

@router.patch(
    "/buildings/{building_id}",
    response_model=BuildingView,
)
def update_building(
    building_id: int,
    payload: BuildingUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    building = get_owned_building(
        db,
        owner.id,
        building_id,
    )

    building.name = payload.name

    db.commit()
    db.refresh(building)

    return building


@router.delete(
    "/buildings/{building_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_building(
    building_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    building = get_owned_building(
        db,
        owner.id,
        building_id,
    )

    unit_count = (
        db.scalar(
            select(
                func.count(
                    Unit.id
                )
            ).where(
                Unit.building_id
                == building_id
            )
        )
        or 0
    )

    if unit_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Delete the building's "
                "units first."
            ),
        )

    db.delete(building)
    db.commit()

    return None


# ---------------------------------
# UNITS
# ---------------------------------

@router.patch(
    "/units/{unit_id}",
    response_model=UnitView,
)
def update_unit(
    unit_id: int,
    payload: UnitUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    unit = get_owned_unit(
        db,
        owner.id,
        unit_id,
    )

    active_lease = db.scalar(
        select(Lease).where(
            Lease.unit_id == unit.id,
            Lease.status
            == LeaseStatus.ACTIVE,
        )
    )

    changes = payload.model_dump(
        exclude_unset=True,
    )

    if "status" in changes:
        requested_status = (
            changes["status"]
        )

        if active_lease:
            if (
                requested_status
                != UnitStatus.OCCUPIED
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "This unit has an active "
                        "lease and must remain "
                        "OCCUPIED."
                    ),
                )

        else:
            if (
                requested_status
                == UnitStatus.OCCUPIED
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "Create an active lease "
                        "instead of setting a unit "
                        "to OCCUPIED manually."
                    ),
                )

    for (
        field,
        value,
    ) in changes.items():
        setattr(
            unit,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(unit)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This unit number already "
                "exists in the building."
            ),
        )

    return unit


@router.delete(
    "/units/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_unit(
    unit_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    unit = get_owned_unit(
        db,
        owner.id,
        unit_id,
    )

    if (
        unit.status
        != UnitStatus.VACANT
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only VACANT units can "
                "be deleted."
            ),
        )

    lease_count = (
        db.scalar(
            select(
                func.count(
                    Lease.id
                )
            ).where(
                Lease.unit_id
                == unit.id
            )
        )
        or 0
    )

    maintenance_count = (
        db.scalar(
            select(
                func.count(
                    Maintenance.id
                )
            ).where(
                Maintenance.unit_id
                == unit.id
            )
        )
        or 0
    )

    expense_count = (
        db.scalar(
            select(
                func.count(
                    Expense.id
                )
            ).where(
                Expense.unit_id
                == unit.id
            )
        )
        or 0
    )

    if (
        lease_count
        or maintenance_count
        or expense_count
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This unit has historical "
                "records and cannot be deleted."
            ),
        )

    db.delete(unit)
    db.commit()

    return None


@router.get(
    "/owner/units/{unit_id}/occupancy",
    response_model=UnitOccupancyView,
)
def get_unit_occupancy(
    unit_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    unit = get_owned_unit(
        db,
        owner.id,
        unit_id,
    )

    statement = (
        select(
            Lease,
            User,
        )
        .join(
            User,
            Lease.tenant_user_id
            == User.id,
        )
        .where(
            Lease.unit_id
            == unit.id,
            Lease.status
            == LeaseStatus.ACTIVE,
        )
    )

    row = db.execute(
        statement
    ).first()

    if row is None:
        return {
            "occupied": False,
            "lease": None,
            "tenant": None,
        }

    lease, tenant = row

    return {
        "occupied": True,
        "lease": lease,
        "tenant": tenant,
    }


# ---------------------------------
# LEASES
# ---------------------------------

@router.patch(
    "/leases/{lease_id}",
    response_model=LeaseCore,
)
def update_lease(
    lease_id: int,
    payload: LeaseUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    lease = get_owned_lease(
        db,
        owner.id,
        lease_id,
    )

    if (
        lease.status
        == LeaseStatus.ENDED
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ended leases are historical "
                "records and cannot be edited."
            ),
        )

    changes = payload.model_dump(
        exclude_unset=True,
    )

    new_start = changes.get(
        "start_date",
        lease.start_date,
    )

    new_end = changes.get(
        "end_date",
        lease.end_date,
    )

    if (
        new_end is not None
        and new_end < new_start
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Lease end date cannot be "
                "before its start date."
            ),
        )

    for (
        field,
        value,
    ) in changes.items():
        setattr(
            lease,
            field,
            value,
        )

    db.commit()
    db.refresh(lease)

    return lease


# ---------------------------------
# MAINTENANCE
# ---------------------------------

@router.patch(
    "/maintenance/{maintenance_id}",
)
def update_maintenance(
    maintenance_id: int,
    payload: MaintenanceUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    maintenance = (
        get_owned_maintenance(
            db,
            owner.id,
            maintenance_id,
        )
    )

    if (
        maintenance.status
        == MaintenanceStatus.RESOLVED
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Resolved maintenance "
                "records cannot be edited."
            ),
        )

    for (
        field,
        value,
    ) in payload.model_dump(
        exclude_unset=True,
    ).items():
        setattr(
            maintenance,
            field,
            value,
        )

    db.commit()
    db.refresh(maintenance)

    return maintenance


@router.delete(
    "/maintenance/{maintenance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_maintenance(
    maintenance_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    maintenance = (
        get_owned_maintenance(
            db,
            owner.id,
            maintenance_id,
        )
    )

    if (
        maintenance.status
        != MaintenanceStatus.OPEN
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only OPEN maintenance "
                "requests may be deleted."
            ),
        )

    linked_expenses = (
        db.scalar(
            select(
                func.count(
                    Expense.id
                )
            ).where(
                Expense.maintenance_id
                == maintenance.id
            )
        )
        or 0
    )

    if linked_expenses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This maintenance request "
                "has linked expenses and "
                "cannot be deleted."
            ),
        )

    db.delete(maintenance)
    db.commit()

    return None


# ---------------------------------
# EXPENSES
# ---------------------------------

@router.patch(
    "/expenses/{expense_id}",
)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    expense = get_owned_expense(
        db,
        owner.id,
        expense_id,
    )

    changes = payload.model_dump(
        exclude_unset=True,
    )

    if "unit_id" in changes:
        requested_unit_id = (
            changes["unit_id"]
        )

        if (
            requested_unit_id
            is not None
        ):
            unit = get_owned_unit(
                db,
                owner.id,
                requested_unit_id,
            )

            building = (
                get_owned_building(
                    db,
                    owner.id,
                    unit.building_id,
                )
            )

            if (
                building.property_id
                != expense.property_id
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                    detail=(
                        "The selected unit "
                        "does not belong to "
                        "this property."
                    ),
                )

    for (
        field,
        value,
    ) in changes.items():
        setattr(
            expense,
            field,
            value,
        )

    db.commit()
    db.refresh(expense)

    return expense


@router.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    expense = get_owned_expense(
        db,
        owner.id,
        expense_id,
    )

    db.delete(expense)
    db.commit()

    return None


# ---------------------------------
# RENT OBLIGATIONS
# ---------------------------------

@router.patch(
    "/rent-obligations/{obligation_id}",
)
def update_rent_obligation(
    obligation_id: int,
    payload: RentObligationUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    obligation = (
        get_owned_obligation(
            db,
            owner.id,
            obligation_id,
        )
    )

    if (
        obligation.status
        != RentObligationStatus.PENDING
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only PENDING rent "
                "obligations may be edited."
            ),
        )

    lease = get_owned_lease(
        db,
        owner.id,
        obligation.lease_id,
    )

    changes = payload.model_dump(
        exclude_unset=True,
    )

    requested_due_date = (
        changes.get(
            "due_date",
            obligation.due_date,
        )
    )

    if (
        requested_due_date
        < lease.start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Due date cannot be before "
                "the lease start date."
            ),
        )

    if (
        lease.end_date is not None
        and requested_due_date
        > lease.end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Due date cannot be after "
                "the lease end date."
            ),
        )

    for (
        field,
        value,
    ) in changes.items():
        setattr(
            obligation,
            field,
            value,
        )

    db.commit()
    db.refresh(obligation)

    return obligation


@router.delete(
    "/rent-obligations/{obligation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rent_obligation(
    obligation_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    obligation = (
        get_owned_obligation(
            db,
            owner.id,
            obligation_id,
        )
    )

    if (
        obligation.status
        != RentObligationStatus.PENDING
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only PENDING rent "
                "obligations may be deleted."
            ),
        )

    db.delete(obligation)
    db.commit()

    return None