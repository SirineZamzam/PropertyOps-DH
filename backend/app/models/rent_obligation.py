import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RentObligationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"


class RentObligation(Base):
    __tablename__ = "rent_obligations"

    __table_args__ = (
        UniqueConstraint(
            "lease_id",
            "due_date",
            name="uq_rent_obligation_lease_due_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    lease_id: Mapped[int] = mapped_column(
        ForeignKey("leases.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[RentObligationStatus] = mapped_column(
        Enum(
            RentObligationStatus,
            name="rent_obligation_status",
        ),
        nullable=False,
        default=RentObligationStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    lease = relationship(
        "Lease",
        back_populates="rent_obligations",
    )