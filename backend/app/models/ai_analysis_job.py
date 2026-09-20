import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class AIAnalysisScope(
    str,
    enum.Enum,
):
    PROPERTY = "PROPERTY"
    UNIT = "UNIT"


class AIJobStatus(
    str,
    enum.Enum,
):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AIAnalysisJob(Base):
    __tablename__ = "ai_analysis_jobs"

    __table_args__ = (
        CheckConstraint(
            "("
            "scope_type = 'PROPERTY' "
            "AND property_id IS NOT NULL "
            "AND unit_id IS NULL"
            ") OR ("
            "scope_type = 'UNIT' "
            "AND unit_id IS NOT NULL "
            "AND property_id IS NULL"
            ")",
            name="ck_ai_job_scope_target",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    owner_user_id: Mapped[int] = (
        mapped_column(
            ForeignKey("users.id"),
            nullable=False,
            index=True,
        )
    )

    scope_type: Mapped[
        AIAnalysisScope
    ] = mapped_column(
        Enum(
            AIAnalysisScope,
            name="ai_analysis_scope",
        ),
        nullable=False,
    )

    property_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey("properties.id"),
        nullable=True,
        index=True,
    )

    unit_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey("units.id"),
        nullable=True,
        index=True,
    )

    status: Mapped[
        AIJobStatus
    ] = mapped_column(
        Enum(
            AIJobStatus,
            name="ai_job_status",
        ),
        nullable=False,
        default=AIJobStatus.PENDING,
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    started_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )