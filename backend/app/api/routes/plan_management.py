from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_admin,
)
from app.db.session import get_db
from app.models.owner_subscription import (
    OwnerSubscription,
)
from app.models.subscription_plan import (
    SubscriptionPlan,
)
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanRead,
    SubscriptionPlanUpdate,
)
from app.services.subscriptions import (
    ensure_default_plans,
)


router = APIRouter()


SYSTEM_PLAN_CODES = {
    "FREE",
    "STANDARD",
    "PRO",
}


def get_plan(
    db: Session,
    plan_id: int,
) -> SubscriptionPlan:
    plan = db.get(
        SubscriptionPlan,
        plan_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Subscription plan "
                "not found."
            ),
        )

    return plan


@router.get(
    "/admin/plans",
    response_model=list[
        SubscriptionPlanRead
    ],
)
def list_admin_plans(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    ensure_default_plans(db)
    db.commit()

    return list(
        db.scalars(
            select(
                SubscriptionPlan
            ).order_by(
                SubscriptionPlan.sort_order,
                SubscriptionPlan.id,
            )
        ).all()
    )


@router.post(
    "/admin/plans",
    response_model=(
        SubscriptionPlanRead
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def create_plan(
    payload: SubscriptionPlanCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    ensure_default_plans(db)

    existing = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.code
            == payload.code
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "A plan with this code "
                "already exists."
            ),
        )

    plan = SubscriptionPlan(
        **payload.model_dump(),
    )

    db.add(plan)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Unable to create plan "
                "because the code already exists."
            ),
        )

    db.refresh(plan)

    return plan


@router.patch(
    "/admin/plans/{plan_id}",
    response_model=(
        SubscriptionPlanRead
    ),
)
def update_plan(
    plan_id: int,
    payload: SubscriptionPlanUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    plan = get_plan(
        db,
        plan_id,
    )

    changes = payload.model_dump(
        exclude_unset=True,
    )

    if (
        plan.code == "FREE"
        and changes.get(
            "is_active"
        ) is False
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "The FREE plan is the "
                "current default signup plan "
                "and cannot be deactivated yet."
            ),
        )

    for (
        field,
        value,
    ) in changes.items():
        setattr(
            plan,
            field,
            value,
        )

    db.commit()
    db.refresh(plan)

    return plan


@router.delete(
    "/admin/plans/{plan_id}",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def delete_plan(
    plan_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    plan = get_plan(
        db,
        plan_id,
    )

    if (
        plan.code
        in SYSTEM_PLAN_CODES
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "System plans cannot be "
                "deleted. Deactivate the "
                "plan instead."
            ),
        )

    subscription_count = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            ).where(
                OwnerSubscription.plan_id
                == plan.id
            )
        )
        or 0
    )

    if subscription_count:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This plan is already in "
                "use. Deactivate it instead."
            ),
        )

    db.delete(plan)
    db.commit()

    return None
