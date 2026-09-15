from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.building import Building
from app.models.property import Property
from app.models.unit import Unit


def get_owned_property(
    db: Session,
    owner_id: int,
    property_id: int,
) -> Property:
    statement = select(Property).where(
        Property.id == property_id,
        Property.owner_id == owner_id,
    )

    property_record = db.scalar(statement)

    if property_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found.",
        )

    return property_record


def get_owned_building(
    db: Session,
    owner_id: int,
    building_id: int,
) -> Building:
    statement = (
        select(Building)
        .join(Property)
        .where(
            Building.id == building_id,
            Property.owner_id == owner_id,
        )
    )

    building = db.scalar(statement)

    if building is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found.",
        )

    return building


def get_owned_unit(
    db: Session,
    owner_id: int,
    unit_id: int,
) -> Unit:
    statement = (
        select(Unit)
        .join(Building)
        .join(Property)
        .where(
            Unit.id == unit_id,
            Property.owner_id == owner_id,
        )
    )

    unit = db.scalar(statement)

    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found.",
        )

    return unit