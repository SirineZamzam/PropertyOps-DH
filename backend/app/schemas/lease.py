from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.lease import LeaseStatus


class LeaseCreate(BaseModel):
    tenant_user_id: int
    start_date: date
    end_date: date | None = None
    rent_amount: Decimal = Field(gt=0, decimal_places=2)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError(
                "End date cannot be before start date."
            )

        return self


class LeaseRead(BaseModel):
    id: int
    unit_id: int
    tenant_user_id: int
    start_date: date
    end_date: date | None
    rent_amount: Decimal
    status: LeaseStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)