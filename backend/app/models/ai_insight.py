from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey(
            "ai_analysis_jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    finding: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    qualification: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    recommendation: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    explanation: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )