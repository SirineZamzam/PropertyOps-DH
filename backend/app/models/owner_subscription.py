import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class SubscriptionStatus(str, enum.Enum):
    FREE = "FREE"
    ACTIVE = "ACTIVE"
    INCOMPLETE = "INCOMPLETE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"


class BillingInterval(str, enum.Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class OwnerSubscription(Base):
    __tablename__ = "owner_subscriptions"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            name="uq_owner_subscriptions_owner_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey(
            "subscription_plans.id",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[
        SubscriptionStatus
    ] = mapped_column(
        Enum(
            SubscriptionStatus,
            name="subscription_status",
        ),
        default=SubscriptionStatus.FREE,
        nullable=False,
    )

    billing_interval: Mapped[
        BillingInterval | None
    ] = mapped_column(
        Enum(
            BillingInterval,
            name="billing_interval",
        ),
        nullable=True,
    )

    stripe_customer_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    stripe_subscription_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    current_period_end: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancel_at_period_end: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
