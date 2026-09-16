from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    unit_id: int | None = None

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    expense_date: date

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class ExpenseRead(BaseModel):
    id: int
    property_id: int
    unit_id: int | None
    maintenance_id: int | None
    amount: Decimal
    category: str
    expense_date: date
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)