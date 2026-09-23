from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_subscription_plans_code",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    monthly_price: Mapped[
        Decimal
    ] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    yearly_price: Mapped[
        Decimal
    ] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    max_properties: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
