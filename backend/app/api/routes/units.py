from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.unit import Unit
from app.models.user import User
from app.schemas.unit import UnitCreate, UnitRead
from app.services.ownership import (
    get_owned_building,
    get_owned_unit,
)


router = APIRouter()


@router.post(
    "/buildings/{building_id}/units",
    response_model=UnitRead,
    status_code=status.HTTP_201_CREATED,
)
def create_unit(
    building_id: int,
    payload: UnitCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> Unit:
    get_owned_building(
        db,
        current_owner.id,
        building_id,
    )

    unit = Unit(
        building_id=building_id,
        unit_number=payload.unit_number,
        status=payload.status,
    )

    db.add(unit)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A unit with this number already exists in this building.",
        )

    db.refresh(unit)

    return unit


@router.get(
    "/buildings/{building_id}/units",
    response_model=list[UnitRead],
)
def list_units(
    building_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> list[Unit]:
    get_owned_building(
        db,
        current_owner.id,
        building_id,
    )

    statement = (
        select(Unit)
        .where(Unit.building_id == building_id)
        .order_by(Unit.unit_number)
    )

    return list(db.scalars(statement).all())


@router.get(
    "/units/{unit_id}",
    response_model=UnitRead,
)
def get_unit(
    unit_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> Unit:
    return get_owned_unit(
        db,
        current_owner.id,
        unit_id,
    )