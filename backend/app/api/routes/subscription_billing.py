from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_owner,
)
from app.db.session import get_db
from app.models.owner_subscription import (
    OwnerSubscription,
    SubscriptionStatus,
)
from app.models.subscription_plan import (
    SubscriptionPlan,
)
from app.models.user import User
from app.schemas.subscription_billing import (
    SubscriptionBillingRead,
    SubscriptionCheckoutRequest,
    SubscriptionCheckoutResponse,
)
from app.services.subscription_billing import (
    create_subscription_checkout,
)
from app.services.subscriptions import (
    get_owner_subscription,
)


router = APIRouter()


@router.post(
    "/owner/subscription/checkout",
    response_model=(
        SubscriptionCheckoutResponse
    ),
)
def create_owner_subscription_checkout(
    payload: SubscriptionCheckoutRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    plan = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.id
            == payload.plan_id,
        )
    )

    if (
        plan is None
        or not plan.is_active
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Subscription plan "
                "not available."
            ),
        )

    if plan.code == "FREE":
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "The FREE plan does not "
                "require Stripe Checkout."
            ),
        )

    (
        subscription,
        _,
    ) = get_owner_subscription(
        db,
        owner.id,
    )

    if (
        subscription
        .stripe_subscription_id
        and subscription.status
        in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
            SubscriptionStatus.INCOMPLETE,
        }
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This owner already has "
                "a Stripe subscription."
            ),
        )

    subscription.plan_id = (
        plan.id
    )

    subscription.billing_interval = (
        payload.billing_interval
    )

    subscription.status = (
        SubscriptionStatus.INCOMPLETE
    )

    db.commit()
    db.refresh(subscription)

    try:
        checkout = (
            create_subscription_checkout(
                owner=owner,
                subscription=subscription,
                plan=plan,
                billing_interval=(
                    payload.billing_interval
                ),
            )
        )
    except Exception as exc:
        subscription.status = (
            SubscriptionStatus.FREE
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to start Stripe "
                "subscription Checkout."
            ),
        ) from exc

    if not checkout.url:
        subscription.status = (
            SubscriptionStatus.FREE
        )
        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Stripe did not return "
                "a Checkout URL."
            ),
        )

    return SubscriptionCheckoutResponse(
        checkout_url=checkout.url,
    )


@router.get(
    "/owner/subscription/billing",
    response_model=(
        SubscriptionBillingRead
    ),
)
def get_owner_subscription_billing(
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
        _,
    ) = get_owner_subscription(
        db,
        owner.id,
    )

    db.commit()

    return SubscriptionBillingRead(
        status=subscription.status,
        billing_interval=(
            subscription.billing_interval
        ),
        current_period_end=(
            subscription.current_period_end
        ),
        cancel_at_period_end=(
            subscription.cancel_at_period_end
        ),
        stripe_subscription_id=(
            subscription.stripe_subscription_id
        ),
    )
