from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BuildingCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class BuildingRead(BaseModel):
    id: int
    property_id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)