from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.unit import UnitStatus


class UnitCreate(BaseModel):
    unit_number: str = Field(min_length=1, max_length=50)
    status: UnitStatus = UnitStatus.VACANT


class UnitRead(BaseModel):
    id: int
    building_id: int
    unit_number: str
    status: UnitStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)