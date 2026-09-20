import enum

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class AIEvidenceType(
    str,
    enum.Enum,
):
    MAINTENANCE = "MAINTENANCE"
    EXPENSE = "EXPENSE"


class AIInsightEvidence(Base):
    __tablename__ = (
        "ai_insight_evidence"
    )

    __table_args__ = (
        UniqueConstraint(
            "insight_id",
            "evidence_type",
            "evidence_id",
            name="uq_ai_insight_evidence",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    insight_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "ai_insights.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            index=True,
        )
    )

    evidence_type: Mapped[
        AIEvidenceType
    ] = mapped_column(
        Enum(
            AIEvidenceType,
            name="ai_evidence_type",
        ),
        nullable=False,
    )

    evidence_id: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
        )
    )