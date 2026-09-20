import enum
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.ai_analysis_job import (
    AIAnalysisScope,
    AIJobStatus,
)

from app.models.ai_insight_evidence import (
    AIEvidenceType,
)


class AIQualification(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# --------------------------------------------------
# Gemini structured output schemas
# --------------------------------------------------

class AIEvidenceReference(BaseModel):
    evidence_type: AIEvidenceType

    evidence_id: int = Field(
        description=(
            "ID of a maintenance or "
            "expense record supplied "
            "in the input data."
        ),
    )

    @field_validator("evidence_id")
    @classmethod
    def validate_evidence_id(
        cls,
        value: int,
    ) -> int:
        if value <= 0:
            raise ValueError(
                "Evidence ID must be positive."
            )

        return value


class AIAnalysisResult(BaseModel):
    finding: str = Field(
        description=(
            "Concise operational "
            "problem or pattern found."
        ),
    )

    qualification: AIQualification = Field(
        description=(
            "Strength of evidence "
            "supporting the finding."
        ),
    )

    recommendation: str | None = Field(
        default=None,
        description=(
            "Practical action the "
            "property owner may "
            "consider. Null when "
            "evidence is weak."
        ),
    )

    explanation: str = Field(
        description=(
            "Brief explanation based "
            "only on supplied records."
        ),
    )

    evidence: list[
        AIEvidenceReference
    ] = Field(
        default_factory=list,
        max_length=12,
        description=(
            "Maintenance and expense "
            "records supporting the "
            "analysis."
        ),
    )

    @field_validator("finding")
    @classmethod
    def validate_finding(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if len(value) < 5:
            raise ValueError(
                "Finding is too short."
            )

        if len(value) > 500:
            raise ValueError(
                "Finding is too long."
            )

        return value

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        if len(value) > 700:
            raise ValueError(
                "Recommendation is too long."
            )

        return value

    @field_validator("explanation")
    @classmethod
    def validate_explanation(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if len(value) < 10:
            raise ValueError(
                "Explanation is too short."
            )

        if len(value) > 1200:
            raise ValueError(
                "Explanation is too long."
            )

        return value


# --------------------------------------------------
# API response schemas
# --------------------------------------------------

class AIInsightEvidenceRead(BaseModel):
    id: int

    evidence_type: AIEvidenceType

    # Kept internally for linking and validation.
    evidence_id: int

    # Human-friendly evidence information.
    evidence_date: date | datetime | None = None

    category: str | None = None

    description: str | None = None

    status: str | None = None

    amount: str | None = None

    unit_id: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class AIInsightRead(BaseModel):
    id: int
    job_id: int

    finding: str

    qualification: AIQualification

    recommendation: str | None

    explanation: str

    created_at: datetime

    evidence: list[
        AIInsightEvidenceRead
    ] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


class AIJobRead(BaseModel):
    id: int

    owner_user_id: int

    scope_type: AIAnalysisScope

    property_id: int | None

    unit_id: int | None

    status: AIJobStatus

    error_message: str | None

    created_at: datetime

    started_at: datetime | None

    completed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class AIJobDetail(AIJobRead):
    insight: AIInsightRead | None = None