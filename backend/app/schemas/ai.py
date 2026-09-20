import enum

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.models.ai_insight_evidence import (
    AIEvidenceType,
)


class AIQualification(
    str,
    enum.Enum,
):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AIEvidenceReference(BaseModel):
    evidence_type: AIEvidenceType

    evidence_id: int = Field(
        description=(
            "ID of a maintenance or "
            "expense record supplied "
            "in the input data."
        ),
    )

    @field_validator(
        "evidence_id"
    )
    @classmethod
    def validate_evidence_id(
        cls,
        value: int,
    ) -> int:
        if value <= 0:
            raise ValueError(
                "Evidence ID must "
                "be positive."
            )

        return value


class AIAnalysisResult(BaseModel):
    finding: str = Field(
        description=(
            "Concise operational "
            "problem or pattern found."
        ),
    )

    qualification: AIQualification = (
        Field(
            description=(
                "Strength of evidence "
                "supporting the finding."
            ),
        )
    )

    recommendation: str | None = (
        Field(
            default=None,
            description=(
                "Practical action the "
                "property owner may "
                "consider. Null when "
                "evidence is weak."
            ),
        )
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

    @field_validator(
        "finding"
    )
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

    @field_validator(
        "recommendation"
    )
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
                "Recommendation "
                "is too long."
            )

        return value

    @field_validator(
        "explanation"
    )
    @classmethod
    def validate_explanation(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if len(value) < 10:
            raise ValueError(
                "Explanation is "
                "too short."
            )

        if len(value) > 1200:
            raise ValueError(
                "Explanation is "
                "too long."
            )

        return value