from dataclasses import dataclass

from app.schemas.ai import (
    AIQualification,
)
from app.services.ai_service import (
    analyze_operational_context,
)
from app.services.ai_worker import (
    validate_ai_evidence,
)


@dataclass
class EvalCase:
    name: str
    context: dict
    allowed_qualifications: set[
        AIQualification
    ]
    recommendation_required: bool


EVAL_CASES = [
    EvalCase(
        name="recurring_plumbing_problem",
        context={
            "scope": {
                "type": "PROPERTY",
                "property_id": 1,
            },
            "maintenance": [
                {
                    "id": 101,
                    "category": "Plumbing",
                    "description": (
                        "Kitchen sink leaking."
                    ),
                    "status": "RESOLVED",
                    "created_at": "2026-04-10",
                },
                {
                    "id": 102,
                    "category": "Plumbing",
                    "description": (
                        "Kitchen pipe leaking again."
                    ),
                    "status": "RESOLVED",
                    "created_at": "2026-06-18",
                },
                {
                    "id": 103,
                    "category": "Plumbing",
                    "description": (
                        "New leak below kitchen sink."
                    ),
                    "status": "OPEN",
                    "created_at": "2026-09-15",
                },
            ],
            "expenses": [
                {
                    "id": 201,
                    "category": "Repair",
                    "description": (
                        "Plumbing repair."
                    ),
                    "amount": "120.00",
                    "created_at": "2026-04-11",
                },
                {
                    "id": 202,
                    "category": "Repair",
                    "description": (
                        "Kitchen pipe repair."
                    ),
                    "amount": "180.00",
                    "created_at": "2026-06-19",
                },
            ],
        },
        allowed_qualifications={
            AIQualification.MEDIUM,
            AIQualification.HIGH,
        },
        recommendation_required=True,
    ),
    EvalCase(
        name="single_resolved_issue",
        context={
            "scope": {
                "type": "PROPERTY",
                "property_id": 2,
            },
            "maintenance": [
                {
                    "id": 301,
                    "category": "Electrical",
                    "description": (
                        "Hallway light stopped working."
                    ),
                    "status": "RESOLVED",
                    "created_at": "2026-05-01",
                },
            ],
            "expenses": [
                {
                    "id": 401,
                    "category": "Repair",
                    "description": (
                        "Replaced hallway light fixture."
                    ),
                    "amount": "45.00",
                    "created_at": "2026-05-02",
                },
            ],
        },
        allowed_qualifications={
            AIQualification.LOW,
        },
        recommendation_required=False,
    ),
    EvalCase(
        name="recurring_hvac_history",
        context={
            "scope": {
                "type": "UNIT",
                "property_id": 3,
                "unit_id": 12,
            },
            "maintenance": [
                {
                    "id": 501,
                    "category": "HVAC",
                    "description": (
                        "Air conditioner stopped cooling."
                    ),
                    "status": "RESOLVED",
                    "created_at": "2026-03-05",
                },
                {
                    "id": 502,
                    "category": "HVAC",
                    "description": (
                        "Air conditioner cooling issue "
                        "returned."
                    ),
                    "status": "RESOLVED",
                    "created_at": "2026-07-08",
                },
                {
                    "id": 503,
                    "category": "HVAC",
                    "description": (
                        "Air conditioner making noise "
                        "and cooling poorly."
                    ),
                    "status": "OPEN",
                    "created_at": "2026-09-18",
                },
            ],
            "expenses": [],
        },
        allowed_qualifications={
            AIQualification.MEDIUM,
            AIQualification.HIGH,
        },
        recommendation_required=True,
    ),
]


def run_case(
    case: EvalCase,
) -> bool:
    print(
        f"\n--- {case.name} ---"
    )

    try:
        result = (
            analyze_operational_context(
                case.context
            )
        )

        validate_ai_evidence(
            result,
            case.context,
        )

        print(
            f"Finding: {result.finding}"
        )
        print(
            "Qualification: "
            f"{result.qualification.value}"
        )
        print(
            "Recommendation: "
            f"{result.recommendation}"
        )
        print(
            "Evidence: "
            f"{[
                (
                    item.evidence_type.value,
                    item.evidence_id,
                )
                for item in result.evidence
            ]}"
        )

        if (
            result.qualification
            not in case.allowed_qualifications
        ):
            print(
                "FAIL: unexpected "
                "qualification."
            )
            return False

        if (
            case.recommendation_required
            and not result.recommendation
        ):
            print(
                "FAIL: recommendation "
                "was expected."
            )
            return False

        if (
            not case.recommendation_required
            and result.recommendation
            is not None
        ):
            print(
                "FAIL: recommendation "
                "should be null."
            )
            return False

        print("PASS")
        return True

    except Exception as exc:
        print(
            f"FAIL: {exc}"
        )
        return False


def main() -> None:
    print(
        "PropertyOps AI Evaluation Suite"
    )

    passed = 0

    for case in EVAL_CASES:
        if run_case(case):
            passed += 1

    total = len(
        EVAL_CASES
    )

    print(
        f"\nResult: {passed}/{total} "
        "evaluation cases passed."
    )

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()