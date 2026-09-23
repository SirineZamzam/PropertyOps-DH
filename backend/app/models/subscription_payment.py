import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class SubscriptionPaymentStatus(
    str,
    enum.Enum,
):
    PAID = "PAID"
    FAILED = "FAILED"


class SubscriptionPayment(Base):
    __tablename__ = "subscription_payments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    owner_subscription_id: Mapped[int] = mapped_column(
        ForeignKey(
            "owner_subscriptions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
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

    stripe_invoice_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
    )

    status: Mapped[
        SubscriptionPaymentStatus
    ] = mapped_column(
        Enum(
            SubscriptionPaymentStatus,
            name="subscription_payment_status",
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
