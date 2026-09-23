from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminPageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class AdminOverviewRead(BaseModel):
    total_owners: int
    active_owners: int
    inactive_owners: int
    total_properties: int
    total_units: int


class AdminOwnerItem(BaseModel):
    id: int

    first_name: str | None
    last_name: str | None
    phone_number: str | None

    email: EmailStr
    is_active: bool
    created_at: datetime

    property_count: int
    building_count: int
    unit_count: int
    active_lease_count: int


class AdminOwnerPage(BaseModel):
    items: list[
        AdminOwnerItem
    ]

    meta: AdminPageMeta


class AdminOwnerStatusUpdate(BaseModel):
    is_active: bool
