import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UnitStatus(str, enum.Enum):
    VACANT = "VACANT"
    OCCUPIED = "OCCUPIED"
    UNAVAILABLE = "UNAVAILABLE"


class Unit(Base):
    __tablename__ = "units"

    __table_args__ = (
        UniqueConstraint(
            "building_id",
            "unit_number",
            name="uq_units_building_unit_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id"),
        nullable=False,
        index=True,
    )

    unit_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[UnitStatus] = mapped_column(
        Enum(UnitStatus, name="unit_status"),
        default=UnitStatus.VACANT,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    building = relationship(
        "Building",
        back_populates="units",
    )

    leases = relationship(
    "Lease",
    back_populates="unit",
    )

    expenses = relationship(
    "Expense",
    back_populates="unit",
    )

    maintenance_records = relationship(
    "Maintenance",
    back_populates="unit",
    )