from datetime import (
    datetime,
    timedelta,
    timezone,
)

from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_owner,
)

from app.core.config import settings

from app.db.session import get_db

from app.models.ai_analysis_job import (
    AIAnalysisJob,
    AIAnalysisScope,
    AIJobStatus,
)

from app.models.ai_insight import (
    AIInsight,
)

from app.models.ai_insight_evidence import (
    AIInsightEvidence,
)

from app.models.user import User

from app.schemas.ai import (
    AIInsightRead,
    AIJobDetail,
    AIJobRead,
)

from app.services.ai_context import (
    collect_property_ai_context,
    collect_unit_ai_context,
)

from app.services.ai_worker import (
    process_ai_job,
)


router = APIRouter()


def enforce_ai_rate_limit(
    db: Session,
    owner_id: int,
) -> None:
    window_start = (
        datetime.now(
            timezone.utc
        )
        - timedelta(hours=1)
    )

    request_count = (
        db.scalar(
            select(
                func.count(
                    AIAnalysisJob.id
                )
            )
            .where(
                AIAnalysisJob
                .owner_user_id
                == owner_id,

                AIAnalysisJob
                .created_at
                >= window_start,
            )
        )
        or 0
    )

    if (
        request_count
        >= settings.ai_requests_per_hour
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "AI analysis limit reached. "
                "Please try again later."
            ),
        )


def ensure_no_active_job(
    db: Session,
    *,
    owner_id: int,
    scope_type: AIAnalysisScope,
    property_id: int | None = None,
    unit_id: int | None = None,
) -> None:
    conditions = [
        AIAnalysisJob.owner_user_id
        == owner_id,

        AIAnalysisJob.scope_type
        == scope_type,

        AIAnalysisJob.status.in_(
            [
                AIJobStatus.PENDING,
                AIJobStatus.PROCESSING,
            ]
        ),
    ]

    if (
        scope_type
        == AIAnalysisScope.PROPERTY
    ):
        conditions.append(
            AIAnalysisJob.property_id
            == property_id
        )

    else:
        conditions.append(
            AIAnalysisJob.unit_id
            == unit_id
        )

    active_job = db.scalar(
        select(
            AIAnalysisJob
        ).where(
            *conditions
        )
    )

    if active_job is not None:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "An AI analysis is already "
                "running for this resource."
            ),
        )


def ensure_context_has_data(
    context: dict,
) -> None:
    if (
        not context["maintenance"]
        and not context["expenses"]
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "There is not enough "
                "operational history to "
                "run an AI analysis."
            ),
        )


@router.post(
    "/owner/ai/properties/"
    "{property_id}/analysis",

    response_model=AIJobRead,

    status_code=(
        status.HTTP_202_ACCEPTED
    ),
)
def request_property_analysis(
    property_id: int,

    background_tasks: (
        BackgroundTasks
    ),

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    # Also validates ownership.
    context = (
        collect_property_ai_context(
            db,
            owner_id=owner.id,
            property_id=property_id,
        )
    )

    ensure_context_has_data(
        context
    )

    ensure_no_active_job(
        db,
        owner_id=owner.id,
        scope_type=(
            AIAnalysisScope.PROPERTY
        ),
        property_id=property_id,
    )

    enforce_ai_rate_limit(
        db,
        owner.id,
    )

    job = AIAnalysisJob(
        owner_user_id=owner.id,

        scope_type=(
            AIAnalysisScope.PROPERTY
        ),

        property_id=property_id,

        status=(
            AIJobStatus.PENDING
        ),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_ai_job,
        job.id,
    )

    return job


@router.post(
    "/owner/ai/units/"
    "{unit_id}/analysis",

    response_model=AIJobRead,

    status_code=(
        status.HTTP_202_ACCEPTED
    ),
)
def request_unit_analysis(
    unit_id: int,

    background_tasks: (
        BackgroundTasks
    ),

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    # Also validates ownership.
    context = (
        collect_unit_ai_context(
            db,
            owner_id=owner.id,
            unit_id=unit_id,
        )
    )

    ensure_context_has_data(
        context
    )

    ensure_no_active_job(
        db,
        owner_id=owner.id,
        scope_type=(
            AIAnalysisScope.UNIT
        ),
        unit_id=unit_id,
    )

    enforce_ai_rate_limit(
        db,
        owner.id,
    )

    job = AIAnalysisJob(
        owner_user_id=owner.id,

        scope_type=(
            AIAnalysisScope.UNIT
        ),

        unit_id=unit_id,

        status=(
            AIJobStatus.PENDING
        ),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_ai_job,
        job.id,
    )

    return job


@router.get(
    "/owner/ai/jobs/{job_id}",

    response_model=(
        AIJobDetail
    ),
)
def get_ai_job(
    job_id: int,

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    job = db.scalar(
        select(
            AIAnalysisJob
        )
        .where(
            AIAnalysisJob.id
            == job_id,

            AIAnalysisJob
            .owner_user_id
            == owner.id,
        )
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "AI analysis job "
                "not found."
            ),
        )

    insight = db.scalar(
        select(
            AIInsight
        ).where(
            AIInsight.job_id
            == job.id
        )
    )

    insight_response = None

    if insight is not None:
        evidence = (
            db.scalars(
                select(
                    AIInsightEvidence
                )
                .where(
                    AIInsightEvidence
                    .insight_id
                    == insight.id
                )
                .order_by(
                    AIInsightEvidence.id
                )
            )
            .all()
        )

        insight_response = (
            AIInsightRead(
                id=insight.id,
                job_id=insight.job_id,
                finding=(
                    insight.finding
                ),
                qualification=(
                    insight.qualification
                ),
                recommendation=(
                    insight.recommendation
                ),
                explanation=(
                    insight.explanation
                ),
                created_at=(
                    insight.created_at
                ),
                evidence=list(
                    evidence
                ),
            )
        )

    return AIJobDetail(
        id=job.id,

        owner_user_id=(
            job.owner_user_id
        ),

        scope_type=(
            job.scope_type
        ),

        property_id=(
            job.property_id
        ),

        unit_id=(
            job.unit_id
        ),

        status=job.status,

        error_message=(
            job.error_message
        ),

        created_at=(
            job.created_at
        ),

        started_at=(
            job.started_at
        ),

        completed_at=(
            job.completed_at
        ),

        insight=insight_response,
    )