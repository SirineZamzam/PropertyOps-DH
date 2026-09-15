from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.building import Building
from app.models.user import User
from app.schemas.building import BuildingCreate, BuildingRead
from app.services.ownership import (
    get_owned_building,
    get_owned_property,
)


router = APIRouter()


@router.post(
    "/properties/{property_id}/buildings",
    response_model=BuildingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_building(
    property_id: int,
    payload: BuildingCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> Building:
    get_owned_property(
        db,
        current_owner.id,
        property_id,
    )

    building = Building(
        property_id=property_id,
        name=payload.name,
    )

    db.add(building)
    db.commit()
    db.refresh(building)

    return building


@router.get(
    "/properties/{property_id}/buildings",
    response_model=list[BuildingRead],
)
def list_buildings(
    property_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> list[Building]:
    get_owned_property(
        db,
        current_owner.id,
        property_id,
    )

    statement = (
        select(Building)
        .where(Building.property_id == property_id)
        .order_by(Building.id)
    )

    return list(db.scalars(statement).all())


@router.get(
    "/buildings/{building_id}",
    response_model=BuildingRead,
)
def get_building(
    building_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> Building:
    return get_owned_building(
        db,
        current_owner.id,
        building_id,
    )