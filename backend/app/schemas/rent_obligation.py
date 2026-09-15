from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.rent_obligation import RentObligationStatus


class RentObligationCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    due_date: date


class RentObligationRead(BaseModel):
    id: int
    lease_id: int
    amount: Decimal
    due_date: date
    status: RentObligationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)