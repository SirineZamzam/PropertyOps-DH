from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_owner,
)
from app.db.session import get_db
from app.models.subscription_plan import (
    SubscriptionPlan,
)
from app.models.user import User
from app.schemas.subscription import (
    OwnerSubscriptionRead,
    SubscriptionPlanRead,
)
from app.services.subscriptions import (
    ensure_default_plans,
    get_owner_subscription,
    property_count_for_owner,
)


router = APIRouter()


@router.get(
    "/subscription-plans",
    response_model=list[
        SubscriptionPlanRead
    ],
)
def list_active_plans(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    ensure_default_plans(db)

    return list(
        db.scalars(
            select(
                SubscriptionPlan
            )
            .where(
                SubscriptionPlan.is_active
                .is_(True)
            )
            .order_by(
                SubscriptionPlan.sort_order,
                SubscriptionPlan.id,
            )
        ).all()
    )


@router.get(
    "/owner/subscription",
    response_model=(
        OwnerSubscriptionRead
    ),
)
def owner_subscription(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    (
        subscription,
        plan,
    ) = get_owner_subscription(
        db,
        owner.id,
    )

    db.commit()
    db.refresh(subscription)

    return OwnerSubscriptionRead(
        id=subscription.id,
        owner_id=owner.id,
        status=subscription.status,
        property_count=(
            property_count_for_owner(
                db,
                owner.id,
            )
        ),
        plan=plan,
    )
