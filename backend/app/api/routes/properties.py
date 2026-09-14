from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyRead


router = APIRouter()


@router.post(
    "/",
    response_model=PropertyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db),
) -> Property:
    property_record = Property(**payload.model_dump())

    db.add(property_record)
    db.commit()
    db.refresh(property_record)

    return property_record


@router.get(
    "/",
    response_model=list[PropertyRead],
)
def list_properties(
    db: Session = Depends(get_db),
) -> list[Property]:
    statement = select(Property).order_by(Property.id)

    return list(db.scalars(statement).all())