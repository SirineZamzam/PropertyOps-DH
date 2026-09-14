from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PropertyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    address: str = Field(min_length=3, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)


class PropertyRead(BaseModel):
    id: int
    name: str
    address: str
    city: str | None
    country: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)