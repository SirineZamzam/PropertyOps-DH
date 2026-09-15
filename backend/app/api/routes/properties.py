from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.property import Property
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyRead


router = APIRouter()


@router.post(
    "/",
    response_model=PropertyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_property(
    payload: PropertyCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> Property:
    property_record = Property(
        **payload.model_dump(),
        owner_id=current_owner.id,
    )

    db.add(property_record)
    db.commit()
    db.refresh(property_record)

    return property_record


@router.get(
    "/",
    response_model=list[PropertyRead],
)
def list_properties(
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> list[Property]:
    statement = (
        select(Property)
        .where(Property.owner_id == current_owner.id)
        .order_by(Property.id)
    )

    return list(db.scalars(statement).all())


@router.get(
    "/{property_id}",
    response_model=PropertyRead,
)
def get_property(
    property_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> Property:
    statement = select(Property).where(
        Property.id == property_id,
        Property.owner_id == current_owner.id,
    )

    property_record = db.scalar(statement)

    if property_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found.",
        )

    return property_record