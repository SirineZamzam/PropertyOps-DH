from app.models.ai_insight_evidence import (
    AIEvidenceType,
)

from app.schemas.ai import (
    AIAnalysisResult,
    AIQualification,
)

from app.services.ai_service import (
    build_analysis_prompt,
)


def test_ai_analysis_result_schema():
    result = AIAnalysisResult(
        finding=(
            "Recurring plumbing issue."
        ),

        qualification=(
            AIQualification.HIGH
        ),

        recommendation=(
            "Inspect the plumbing line."
        ),

        explanation=(
            "Three similar incidents "
            "occurred recently."
        ),

        evidence=[
            {
                "evidence_type":
                    AIEvidenceType
                    .MAINTENANCE,

                "evidence_id": 12,
            },

            {
                "evidence_type":
                    AIEvidenceType
                    .EXPENSE,

                "evidence_id": 8,
            },
        ],
    )

    assert (
        result.qualification
        == AIQualification.HIGH
    )

    assert len(
        result.evidence
    ) == 2


def test_ai_result_allows_no_recommendation():
    result = AIAnalysisResult(
        finding=(
            "No meaningful recurring "
            "pattern detected."
        ),

        qualification=(
            AIQualification.LOW
        ),

        recommendation=None,

        explanation=(
            "The available records are "
            "too limited to support a "
            "specific recommendation."
        ),

        evidence=[],
    )

    assert (
        result.recommendation
        is None
    )


def test_analysis_prompt_contains_safety_rules():
    context = {
        "scope": {
            "type": "UNIT",
            "unit_id": 10,
        },
        "maintenance": [],
        "expenses": [],
    }

    prompt = (
        build_analysis_prompt(
            context
        )
    )

    assert (
        "Do not invent facts"
        in prompt
    )

    assert (
        "MAINTENANCE"
        in prompt
    )

    assert (
        "EXPENSE"
        in prompt
    )

    assert (
        '"unit_id": 10'
        in prompt
    )