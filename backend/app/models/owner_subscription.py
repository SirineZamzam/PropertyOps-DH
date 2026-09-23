import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class SubscriptionStatus(
    str,
    enum.Enum,
):
    FREE = "FREE"
    ACTIVE = "ACTIVE"
    INCOMPLETE = "INCOMPLETE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"


class OwnerSubscription(Base):
    __tablename__ = "owner_subscriptions"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            name=(
                "uq_owner_subscriptions_owner_id"
            ),
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
