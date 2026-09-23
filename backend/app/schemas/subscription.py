from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.owner_subscription import (
    BillingInterval,
    SubscriptionStatus,
)


class SubscriptionPlanRead(BaseModel):
    id: int
    code: str
    name: str

    monthly_price: Decimal
    yearly_price: Decimal
    max_properties: int | None

    sort_order: int
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class SubscriptionPlanCreate(BaseModel):
    code: str = Field(
        min_length=2,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    monthly_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    yearly_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    max_properties: int | None = Field(
        default=None,
        ge=1,
    )

    sort_order: int = Field(
        default=0,
        ge=0,
    )

    is_active: bool = True

    @field_validator("code")
    @classmethod
    def normalize_code(
        cls,
        value: str,
    ) -> str:
        return (
            value.strip()
            .upper()
        )

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        return value.strip()


class SubscriptionPlanUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    monthly_price: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    yearly_price: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    max_properties: int | None = Field(
        default=None,
        ge=1,
    )

    sort_order: int | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip()


class OwnerSubscriptionRead(BaseModel):
    id: int
    owner_id: int
    status: SubscriptionStatus
    billing_interval: BillingInterval | None
    current_period_end: datetime | None
    cancel_at_period_end: bool

    property_count: int
    effective_max_properties: int | None

    plan: SubscriptionPlanRead
