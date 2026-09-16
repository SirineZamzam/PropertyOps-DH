from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.maintenance import MaintenanceStatus


class MaintenanceCreate(BaseModel):
    category: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        min_length=5,
        max_length=2000,
    )


class MaintenanceStatusUpdate(BaseModel):
    status: MaintenanceStatus


class MaintenanceRead(BaseModel):
    id: int
    unit_id: int
    created_by_user_id: int
    category: str
    description: str
    status: MaintenanceStatus
    created_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)