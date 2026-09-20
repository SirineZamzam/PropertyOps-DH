import pytest

from app.models.ai_analysis_job import (
    AIAnalysisJob,
    AIAnalysisScope,
    AIJobStatus,
)
from app.models.ai_insight import (
    AIInsight,
)
from app.models.ai_insight_evidence import (
    AIEvidenceType,
    AIInsightEvidence,
)
from app.models.property import Property
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.ai import (
    AIAnalysisResult,
    AIQualification,
)
from app.services import ai_worker


def create_owner(
    db,
) -> User:
    owner = User(
        email="ai.owner@test.com",
        password_hash="test-hash",
        role=UserRole.OWNER,
    )

    db.add(owner)
    db.commit()
    db.refresh(owner)

    return owner


def create_property(
    db,
    owner: User,
) -> Property:
    property_record = Property(
        owner_id=owner.id,
        name="AI Test Property",
        address="10 Test Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(property_record)
    db.commit()
    db.refresh(property_record)

    return property_record


def create_pending_job(
    db,
    owner: User,
    property_record: Property,
) -> AIAnalysisJob:
    job = AIAnalysisJob(
        owner_user_id=owner.id,
        scope_type=(
            AIAnalysisScope.PROPERTY
        ),
        property_id=(
            property_record.id
        ),
        status=AIJobStatus.PENDING,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def test_invalid_ai_evidence_is_rejected():
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
        qualification=(
            AIQualification.HIGH
        ),
        recommendation=(
            "Inspect plumbing."
        ),
        explanation=(
            "Multiple related incidents "
            "were detected."
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
        ai_worker.validate_ai_evidence(
            result,
            context,
        )


def test_ai_worker_saves_valid_insight(
    db,
    monkeypatch,
):
    owner = create_owner(db)

    property_record = (
        create_property(
            db,
            owner,
        )
    )

    job = create_pending_job(
        db,
        owner,
        property_record,
    )
    job_id = job.id

    context = {
        "scope": {
            "type": "PROPERTY",
            "property_id":
                property_record.id,
        },
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

    fake_result = (
        AIAnalysisResult(
            finding=(
                "Recurring plumbing issue."
            ),
            qualification=(
                AIQualification.HIGH
            ),
            recommendation=(
                "Inspect the plumbing."
            ),
            explanation=(
                "Repeated maintenance "
                "and repair costs were "
                "detected."
            ),
            evidence=[
                {
                    "evidence_type":
                        AIEvidenceType
                        .MAINTENANCE,

                    "evidence_id": 10,
                },
                {
                    "evidence_type":
                        AIEvidenceType
                        .EXPENSE,

                    "evidence_id": 20,
                },
            ],
        )
    )

    monkeypatch.setattr(
        ai_worker,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        ai_worker,
        "collect_property_ai_context",
        lambda *args, **kwargs:
            context,
    )

    monkeypatch.setattr(
        ai_worker,
        "analyze_operational_context",
        lambda context:
            fake_result,
    )

    ai_worker.process_ai_job(
        job_id
    )

    updated_job = db.get(
        AIAnalysisJob,
        job_id,
    )

    assert (
        updated_job.status
        == AIJobStatus.COMPLETED
    )

    insight = (
        db.query(AIInsight)
        .filter(
            AIInsight.job_id
            == job_id
        )
        .one()
    )

    assert (
        insight.finding
        == "Recurring plumbing issue."
    )

    evidence = (
        db.query(
            AIInsightEvidence
        )
        .filter(
            AIInsightEvidence
            .insight_id
            == insight.id
        )
        .all()
    )

    assert len(evidence) == 2


def test_ai_worker_failure_marks_job_failed(
    db,
    monkeypatch,
):
    owner = create_owner(db)

    property_record = (
        create_property(
            db,
            owner,
        )
    )

    job = create_pending_job(
        db,
        owner,
        property_record,
    )
    job_id = job.id

    context = {
        "scope": {
            "type": "PROPERTY",
            "property_id":
                property_record.id,
        },
        "maintenance": [
            {
                "id": 10,
            },
        ],
        "expenses": [],
    }

    def fail_ai(
        context,
    ):
        raise RuntimeError(
            "Provider unavailable"
        )

    monkeypatch.setattr(
        ai_worker,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        ai_worker,
        "collect_property_ai_context",
        lambda *args, **kwargs:
            context,
    )

    monkeypatch.setattr(
        ai_worker,
        "analyze_operational_context",
        fail_ai,
    )

    ai_worker.process_ai_job(
        job_id
    )

    updated_job = db.get(
        AIAnalysisJob,
        job_id,
    )

    assert (
        updated_job.status
        == AIJobStatus.FAILED
    )

    assert (
        updated_job.error_message
        is not None
    )