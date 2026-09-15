import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LeaseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class Lease(Base):
    __tablename__ = "leases"

    __table_args__ = (
        Index(
            "uq_active_lease_per_unit",
            "unit_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    unit_id: Mapped[int] = mapped_column(
        ForeignKey("units.id"),
        nullable=False,
        index=True,
    )

    tenant_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    rent_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[LeaseStatus] = mapped_column(
        Enum(LeaseStatus, name="lease_status"),
        nullable=False,
        default=LeaseStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    unit = relationship(
        "Unit",
        back_populates="leases",
    )

    tenant = relationship(
        "User",
        back_populates="leases",
    )

    rent_obligations = relationship(
    "RentObligation",
    back_populates="lease",
    )