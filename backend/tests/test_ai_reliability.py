import pytest

from pydantic import ValidationError

from app.models.ai_insight_evidence import (
    AIEvidenceType,
)

from app.schemas.ai import (
    AIAnalysisResult,
)

from app.services.ai_worker import (
    validate_ai_evidence,
)


def test_valid_structured_ai_result():
    result = AIAnalysisResult(
        finding=(
            "Recurring plumbing leaks "
            "were detected."
        ),
        qualification="HIGH",
        recommendation=(
            "Inspect the plumbing system."
        ),
        explanation=(
            "Multiple related maintenance "
            "events occurred during the "
            "analysis period."
        ),
        evidence=[
            {
                "evidence_type":
                    "MAINTENANCE",

                "evidence_id": 10,
            },
        ],
    )

    assert (
        result.qualification.value
        == "HIGH"
    )

    assert len(
        result.evidence
    ) == 1


def test_malformed_ai_json_is_rejected():
    malformed = """
    {
        this is not valid json
    }
    """

    with pytest.raises(
        ValidationError
    ):
        (
            AIAnalysisResult
            .model_validate_json(
                malformed
            )
        )


def test_missing_required_fields_are_rejected():
    payload = {
        "qualification":
            "HIGH",

        "evidence": [],
    }

    with pytest.raises(
        ValidationError
    ):
        (
            AIAnalysisResult
            .model_validate(
                payload
            )
        )


def test_invalid_qualification_is_rejected():
    payload = {
        "finding":
            "Recurring plumbing issue.",

        "qualification":
            "VERY_HIGH",

        "recommendation":
            None,

        "explanation": (
            "Several related records "
            "were detected."
        ),

        "evidence": [],
    }

    with pytest.raises(
        ValidationError
    ):
        (
            AIAnalysisResult
            .model_validate(
                payload
            )
        )


def test_wrong_field_type_is_rejected():
    payload = {
        "finding":
            "Recurring plumbing issue.",

        "qualification":
            "HIGH",

        "recommendation":
            None,

        "explanation": (
            "Several related records "
            "were detected."
        ),

        "evidence": [
            {
                "evidence_type":
                    "MAINTENANCE",

                "evidence_id":
                    "not-an-id",
            },
        ],
    }

    with pytest.raises(
        ValidationError
    ):
        (
            AIAnalysisResult
            .model_validate(
                payload
            )
        )


def test_nonexistent_evidence_is_rejected():
    context = {
        "maintenance": [
            {
                "id": 10,
            },
        ],

        "expenses": [
            {
                "id": 20,
            },
        ],
    }

    result = AIAnalysisResult(
        finding=(
            "Recurring plumbing issue."
        ),
        qualification="HIGH",
        recommendation=None,
        explanation=(
            "Repeated maintenance "
            "records were detected."
        ),
        evidence=[
            {
                "evidence_type":
                    AIEvidenceType
                    .MAINTENANCE,

                "evidence_id": 999,
            },
        ],
    )

    with pytest.raises(
        ValueError
    ):
        validate_ai_evidence(
            result,
            context,
        )


def test_evidence_outside_property_scope_is_rejected():
    # Context represents only records
    # belonging to the requested property.
    context = {
        "maintenance": [
            {
                "id": 11,
            },
        ],

        "expenses": [
            {
                "id": 21,
            },
        ],
    }

    # ID 55 may exist elsewhere in the
    # database, but it was not supplied
    # for this property.
    result = AIAnalysisResult(
        finding=(
            "Possible recurring issue."
        ),
        qualification="MEDIUM",
        recommendation=None,
        explanation=(
            "The supplied records show "
            "a possible recurring issue."
        ),
        evidence=[
            {
                "evidence_type":
                    "MAINTENANCE",

                "evidence_id": 55,
            },
        ],
    )

    with pytest.raises(
        ValueError
    ):
        validate_ai_evidence(
            result,
            context,
        )


def test_evidence_outside_unit_scope_is_rejected():
    # Context represents only records
    # belonging to one requested unit.
    context = {
        "maintenance": [
            {
                "id": 12,
            },
        ],

        "expenses": [
            {
                "id": 22,
            },
        ],
    }

    # Expense 88 is not part of the
    # requested unit context.
    result = AIAnalysisResult(
        finding=(
            "Possible repeated repair."
        ),
        qualification="MEDIUM",
        recommendation=None,
        explanation=(
            "The supplied unit records "
            "show repeated activity."
        ),
        evidence=[
            {
                "evidence_type":
                    "EXPENSE",

                "evidence_id": 88,
            },
        ],
    )

    with pytest.raises(
        ValueError
    ):
        validate_ai_evidence(
            result,
            context,
        )