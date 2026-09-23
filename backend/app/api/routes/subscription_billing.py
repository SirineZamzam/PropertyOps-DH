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
from app.models.subscription_payment import (
    SubscriptionPayment,
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
from app.schemas.subscription_views import (
    SubscriptionActionRead,
    SubscriptionChangeRequest,
    SubscriptionPaymentItemRead,
)
from app.services.subscription_billing import (
    change_stripe_subscription,
    create_subscription_checkout,
    set_subscription_cancel_at_period_end,
    sync_local_subscription_from_stripe,
)
from app.services.subscriptions import (
    get_owner_subscription,
    get_plan_by_code,
)


router = APIRouter()


def get_available_plan(
    db: Session,
    plan_id: int,
) -> SubscriptionPlan:
    plan = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.id
            == plan_id,
            SubscriptionPlan.is_active
            .is_(True),
        )
    )

    if plan is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Subscription plan "
                "not available."
            ),
        )

    return plan


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
    plan = get_available_plan(
        db,
        payload.plan_id,
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
        free_plan = (
            get_plan_by_code(
                db,
                "FREE",
            )
        )

        subscription.plan_id = (
            free_plan.id
        )
        subscription.status = (
            SubscriptionStatus.FREE
        )
        subscription.billing_interval = None

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
        free_plan = (
            get_plan_by_code(
                db,
                "FREE",
            )
        )

        subscription.plan_id = (
            free_plan.id
        )
        subscription.status = (
            SubscriptionStatus.FREE
        )
        subscription.billing_interval = None

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


@router.post(
    "/owner/subscription/change",
    response_model=SubscriptionActionRead,
)
def change_owner_subscription(
    payload: SubscriptionChangeRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    plan = get_available_plan(
        db,
        payload.plan_id,
    )

    if plan.code == "FREE":
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Use cancellation to move "
                "from a paid plan to FREE."
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
        subscription.status
        != SubscriptionStatus.ACTIVE
        or not subscription
        .stripe_subscription_id
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only an active Stripe "
                "subscription can be changed."
            ),
        )

    try:
        stripe_subscription = (
            change_stripe_subscription(
                subscription=subscription,
                plan=plan,
                billing_interval=(
                    payload.billing_interval
                ),
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to update the Stripe "
                "subscription."
            ),
        ) from exc

    subscription.plan_id = plan.id
    subscription.billing_interval = (
        payload.billing_interval
    )

    sync_local_subscription_from_stripe(
        subscription=subscription,
        stripe_subscription=(
            stripe_subscription
        ),
    )

    db.commit()

    return SubscriptionActionRead(
        message=(
            "Subscription change submitted "
            "to Stripe."
        )
    )


@router.post(
    "/owner/subscription/cancel",
    response_model=SubscriptionActionRead,
)
def cancel_owner_subscription(
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

    if (
        subscription.status
        not in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
        }
        or not subscription
        .stripe_subscription_id
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "There is no active Stripe "
                "subscription to cancel."
            ),
        )

    try:
        stripe_subscription = (
            set_subscription_cancel_at_period_end(
                subscription=subscription,
                cancel_at_period_end=True,
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to schedule Stripe "
                "subscription cancellation."
            ),
        ) from exc

    sync_local_subscription_from_stripe(
        subscription=subscription,
        stripe_subscription=(
            stripe_subscription
        ),
    )

    subscription.cancel_at_period_end = True

    db.commit()

    return SubscriptionActionRead(
        message=(
            "Subscription will cancel at "
            "the end of the current period."
        )
    )


@router.post(
    "/owner/subscription/resume",
    response_model=SubscriptionActionRead,
)
def resume_owner_subscription(
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

    if (
        not subscription
        .stripe_subscription_id
        or not subscription
        .cancel_at_period_end
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This subscription is not "
                "scheduled for cancellation."
            ),
        )

    try:
        stripe_subscription = (
            set_subscription_cancel_at_period_end(
                subscription=subscription,
                cancel_at_period_end=False,
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to keep the Stripe "
                "subscription active."
            ),
        ) from exc

    sync_local_subscription_from_stripe(
        subscription=subscription,
        stripe_subscription=(
            stripe_subscription
        ),
    )

    subscription.cancel_at_period_end = False

    db.commit()

    return SubscriptionActionRead(
        message=(
            "Subscription cancellation "
            "was removed."
        )
    )


@router.post(
    "/owner/subscription/use-free",
    response_model=SubscriptionActionRead,
)
def use_free_plan(
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

    if (
        subscription.status
        in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
            SubscriptionStatus.INCOMPLETE,
        }
        and subscription
        .stripe_subscription_id
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Cancel the active paid "
                "subscription first."
            ),
        )

    free_plan = (
        get_plan_by_code(
            db,
            "FREE",
        )
    )

    subscription.plan_id = (
        free_plan.id
    )
    subscription.status = (
        SubscriptionStatus.FREE
    )
    subscription.billing_interval = None
    subscription.current_period_end = None
    subscription.cancel_at_period_end = False
    subscription.stripe_subscription_id = None

    db.commit()

    return SubscriptionActionRead(
        message="FREE plan is active."
    )


@router.post(
    "/owner/subscription/checkout-cancelled",
    response_model=SubscriptionActionRead,
)
def reset_cancelled_checkout(
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

    if (
        subscription.status
        == SubscriptionStatus.INCOMPLETE
        and not subscription
        .stripe_subscription_id
    ):
        free_plan = (
            get_plan_by_code(
                db,
                "FREE",
            )
        )

        subscription.plan_id = (
            free_plan.id
        )
        subscription.status = (
            SubscriptionStatus.FREE
        )
        subscription.billing_interval = None
        subscription.current_period_end = None
        subscription.cancel_at_period_end = False

        db.commit()

    return SubscriptionActionRead(
        message=(
            "Checkout cancellation handled."
        )
    )


@router.get(
    "/owner/subscription/payments",
    response_model=list[
        SubscriptionPaymentItemRead
    ],
)
def list_owner_subscription_payments(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    rows = db.execute(
        select(
            SubscriptionPayment,
            SubscriptionPlan,
        )
        .join(
            SubscriptionPlan,
            SubscriptionPayment.plan_id
            == SubscriptionPlan.id,
        )
        .where(
            SubscriptionPayment.owner_id
            == owner.id
        )
        .order_by(
            SubscriptionPayment
            .created_at
            .desc()
        )
        .limit(50)
    ).all()

    return [
        SubscriptionPaymentItemRead(
            id=payment.id,
            plan_id=plan.id,
            plan_code=plan.code,
            plan_name=plan.name,
            stripe_invoice_id=(
                payment.stripe_invoice_id
            ),
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            created_at=payment.created_at,
        )
        for (
            payment,
            plan,
        ) in rows
    ]


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
