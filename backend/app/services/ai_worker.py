import logging
from datetime import (
    datetime,
    timezone,
)

from app.db.session import (
    SessionLocal,
)

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

from app.services.ai_context import (
    collect_property_ai_context,
    collect_unit_ai_context,
)

from app.services.ai_service import (
    analyze_operational_context,
)


logger = logging.getLogger(
    __name__
)


def validate_ai_evidence(
    result,
    context: dict,
) -> None:
    maintenance_ids = {
        record["id"]
        for record
        in context["maintenance"]
    }

    expense_ids = {
        record["id"]
        for record
        in context["expenses"]
    }

    for evidence in result.evidence:
        if (
            evidence.evidence_type
            == AIEvidenceType.MAINTENANCE
        ):
            if (
                evidence.evidence_id
                not in maintenance_ids
            ):
                raise ValueError(
                    "AI referenced maintenance "
                    f"record {evidence.evidence_id} "
                    "outside the supplied context."
                )

        elif (
            evidence.evidence_type
            == AIEvidenceType.EXPENSE
        ):
            if (
                evidence.evidence_id
                not in expense_ids
            ):
                raise ValueError(
                    "AI referenced expense "
                    f"record {evidence.evidence_id} "
                    "outside the supplied context."
                )

        else:
            raise ValueError(
                "Unsupported AI evidence type."
            )


def process_ai_job(
    job_id: int,
) -> None:
    db = SessionLocal()

    try:
        job = db.get(
            AIAnalysisJob,
            job_id,
        )

        if job is None:
            logger.warning(
                "AI job %s was not found.",
                job_id,
            )
            return

        if (
            job.status
            != AIJobStatus.PENDING
        ):
            logger.info(
                "AI job %s is no longer "
                "pending.",
                job_id,
            )
            return

        # -------------------------
        # PROCESSING
        # -------------------------

        job.status = (
            AIJobStatus.PROCESSING
        )

        job.started_at = (
            datetime.now(
                timezone.utc
            )
        )

        job.error_message = None

        db.commit()

        # -------------------------
        # COLLECT REAL DATA
        # -------------------------

        if (
            job.scope_type
            == AIAnalysisScope.PROPERTY
        ):
            if job.property_id is None:
                raise RuntimeError(
                    "Property AI job has "
                    "no property ID."
                )

            context = (
                collect_property_ai_context(
                    db,
                    owner_id=(
                        job.owner_user_id
                    ),
                    property_id=(
                        job.property_id
                    ),
                )
            )

        elif (
            job.scope_type
            == AIAnalysisScope.UNIT
        ):
            if job.unit_id is None:
                raise RuntimeError(
                    "Unit AI job has "
                    "no unit ID."
                )

            context = (
                collect_unit_ai_context(
                    db,
                    owner_id=(
                        job.owner_user_id
                    ),
                    unit_id=(
                        job.unit_id
                    ),
                )
            )

        else:
            raise RuntimeError(
                "Unsupported AI scope."
            )

        # -------------------------
        # GEMINI
        # -------------------------

        result = (
            analyze_operational_context(
                context
            )
        )

        # -------------------------
        # DO NOT TRUST AI EVIDENCE
        # -------------------------

        validate_ai_evidence(
            result,
            context,
        )

        # -------------------------
        # SAVE INSIGHT
        # -------------------------

        insight = AIInsight(
            job_id=job.id,
            finding=result.finding,
            qualification=(
                result
                .qualification
                .value
            ),
            recommendation=(
                result.recommendation
            ),
            explanation=(
                result.explanation
            ),
        )

        db.add(insight)

        # We need the generated insight ID
        # before creating evidence rows.
        db.flush()

        seen_evidence = set()

        for evidence in result.evidence:
            evidence_key = (
                evidence.evidence_type,
                evidence.evidence_id,
            )

            if (
                evidence_key
                in seen_evidence
            ):
                continue

            seen_evidence.add(
                evidence_key
            )

            db.add(
                AIInsightEvidence(
                    insight_id=(
                        insight.id
                    ),
                    evidence_type=(
                        evidence
                        .evidence_type
                    ),
                    evidence_id=(
                        evidence
                        .evidence_id
                    ),
                )
            )

        # -------------------------
        # COMPLETED
        # -------------------------

        job.status = (
            AIJobStatus.COMPLETED
        )

        job.completed_at = (
            datetime.now(
                timezone.utc
            )
        )

        job.error_message = None

        db.commit()

        logger.info(
            "AI job %s completed.",
            job.id,
        )

    except Exception:
        db.rollback()

        logger.exception(
            "AI job %s failed.",
            job_id,
        )

        job = db.get(
            AIAnalysisJob,
            job_id,
        )

        if job is not None:
            job.status = (
                AIJobStatus.FAILED
            )

            job.error_message = (
                "AI analysis could not be "
                "completed. Please try again."
            )

            job.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

            db.commit()

    finally:
        db.close()