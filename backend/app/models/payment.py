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


class PaymentStatus(
    str,
    enum.Enum,
):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class PaymentMethod(
    str,
    enum.Enum,
):
    STRIPE = "STRIPE"
    CASH = "CASH"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    rent_obligation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rent_obligations.id",
        ),
        nullable=False,
        index=True,
    )

    tenant_user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
        ),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(
            12,
            2,
        ),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="usd",
    )

    status: Mapped[
        PaymentStatus
    ] = mapped_column(
        Enum(
            PaymentStatus,
            name="payment_status",
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
    )

    payment_method: Mapped[
        PaymentMethod
    ] = mapped_column(
        Enum(
            PaymentMethod,
            name="payment_method",
        ),
        nullable=False,
        default=PaymentMethod.STRIPE,
        server_default="STRIPE",
    )

    manual_note: Mapped[
        str | None
    ] = mapped_column(
        String(500),
        nullable=True,
    )

    stripe_checkout_session_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    stripe_payment_intent_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True,
        ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    paid_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
    )
