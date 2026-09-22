import re

from datetime import (
    date,
    datetime,
)
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.models.lease import LeaseStatus
from app.models.maintenance import (
    MaintenanceStatus,
)
from app.models.rent_obligation import (
    RentObligationStatus,
)
from app.models.unit import (
    UnitStatus,
    UnitType,
)
from app.models.user import UserRole


PHONE_PATTERN = re.compile(
    r"^[0-9+().\-\s]{7,30}$"
)


def validate_phone(
    value: str,
) -> str:
    cleaned = value.strip()

    if not PHONE_PATTERN.fullmatch(
        cleaned
    ):
        raise ValueError(
            "Enter a valid phone number."
        )

    return cleaned


class UserSummary(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class OwnerContact(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
    )

    email: EmailStr | None = None

    @field_validator(
        "first_name",
        "last_name",
    )
    @classmethod
    def clean_name(
        cls,
        value: str | None,
    ):
        if value is None:
            return None

        return value.strip()

    @field_validator(
        "phone_number",
    )
    @classmethod
    def clean_phone(
        cls,
        value: str | None,
    ):
        if value is None:
            return None

        return validate_phone(value)

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class PasswordChange(BaseModel):
    current_password: str = Field(
        min_length=8,
        max_length=128,
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

    @model_validator(mode="after")
    def passwords_must_differ(self):
        if (
            self.current_password
            == self.new_password
        ):
            raise ValueError(
                "New password must be different from the current password."
            )

        return self
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
    )

    @field_validator(
        "first_name",
        "last_name",
    )
    @classmethod
    def clean_name(
        cls,
        value: str | None,
    ):
        if value is None:
            return None

        return value.strip()

    @field_validator(
        "phone_number",
    )
    @classmethod
    def clean_phone(
        cls,
        value: str | None,
    ):
        if value is None:
            return None

        return validate_phone(value)

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class OwnerTenantCreate(BaseModel):
    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    phone_number: str = Field(
        min_length=7,
        max_length=30,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator(
        "first_name",
        "last_name",
    )
    @classmethod
    def clean_name(
        cls,
        value: str,
    ):
        return value.strip()

    @field_validator(
        "phone_number",
    )
    @classmethod
    def clean_phone(
        cls,
        value: str,
    ):
        return validate_phone(value)


class PropertyUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    address: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class BuildingUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )


class UnitUpdate(BaseModel):
    unit_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    unit_type: UnitType | None = None

    status: UnitStatus | None = None

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self
    unit_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    status: UnitStatus | None = None

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class LeaseUpdate(BaseModel):
    start_date: date | None = None

    end_date: date | None = None

    rent_amount: Decimal | None = Field(
        default=None,
        gt=0,
    )

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class MaintenanceUpdate(BaseModel):
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
        max_length=2000,
    )

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class ExpenseUpdate(BaseModel):
    unit_id: int | None = None

    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    expense_date: date | None = None

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class RentObligationUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )

    due_date: date | None = None

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class PropertyView(BaseModel):
    id: int
    owner_id: int
    name: str
    address: str
    city: str
    country: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class BuildingView(BaseModel):
    id: int
    property_id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UnitView(BaseModel):
    id: int
    building_id: int
    unit_number: str
    status: UnitStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class LeaseCore(BaseModel):
    id: int
    unit_id: int
    tenant_user_id: int
    start_date: date
    end_date: date | None
    rent_amount: Decimal
    status: LeaseStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UnitOccupancyView(BaseModel):
    occupied: bool
    lease: LeaseCore | None
    tenant: UserSummary | None


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class OwnerLeaseItem(BaseModel):
    id: int
    status: LeaseStatus
    start_date: date
    end_date: date | None
    rent_amount: Decimal
    created_at: datetime

    property_id: int
    property_name: str

    building_id: int
    building_name: str

    unit_id: int
    unit_number: str

    tenant: UserSummary


class OwnerLeasePage(BaseModel):
    items: list[OwnerLeaseItem]
    meta: PageMeta

class OwnerTenantItem(BaseModel):
    lease_id: int
    tenant: UserSummary

    property_id: int
    property_name: str

    building_id: int
    building_name: str

    unit_id: int
    unit_number: str

    start_date: date
    end_date: date | None
    rent_amount: Decimal


class OwnerTenantPage(BaseModel):
    items: list[OwnerTenantItem]
    meta: PageMeta


class OwnerMaintenanceItem(BaseModel):
    id: int
    category: str
    description: str
    status: MaintenanceStatus
    created_at: datetime
    resolved_at: datetime | None

    property_id: int
    property_name: str

    building_id: int
    building_name: str

    unit_id: int
    unit_number: str

    creator: UserSummary


class OwnerMaintenancePage(BaseModel):
    items: list[OwnerMaintenanceItem]
    meta: PageMeta


class OwnerExpenseItem(BaseModel):
    id: int
    property_id: int  | None
    property_name: str | None

    building_id: int | None
    building_name: str | None

    unit_id: int | None
    unit_number: str | None

    maintenance_id: int | None

    amount: Decimal
    category: str
    expense_date: date
    description: str | None
    created_at: datetime


class OwnerExpensePage(BaseModel):
    items: list[OwnerExpenseItem]
    meta: PageMeta


class OwnerRentItem(BaseModel):
    id: int

    amount: Decimal
    due_date: date
    status: RentObligationStatus
    created_at: datetime

    lease_id: int

    property_id: int
    property_name: str

    building_id: int
    building_name: str

    unit_id: int
    unit_number: str

    tenant: UserSummary


class OwnerRentPage(BaseModel):
    items: list[OwnerRentItem]
    meta: PageMeta


class TenantHomeItem(BaseModel):
    lease_id: int

    property_id: int
    property_name: str

    building_id: int
    building_name: str

    unit_id: int
    unit_number: str

    rent_amount: Decimal
    start_date: date
    end_date: date | None
    owner: OwnerContact