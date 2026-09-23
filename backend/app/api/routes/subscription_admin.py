import math
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_admin,
)
from app.db.session import get_db
from app.models.owner_subscription import (
    OwnerSubscription,
    SubscriptionStatus,
)
from app.models.property import Property
from app.models.subscription_payment import (
    SubscriptionPayment,
    SubscriptionPaymentStatus,
)
from app.models.subscription_plan import (
    SubscriptionPlan,
)
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.subscription_views import (
    AdminSubscriptionItemRead,
    AdminSubscriptionPage,
    AdminSubscriptionPaymentItemRead,
    AdminSubscriptionPaymentPage,
    AdminSubscriptionSummaryRead,
    PageMeta,
)


router = APIRouter()


def make_meta(
    page: int,
    page_size: int,
    total: int,
) -> PageMeta:
    return PageMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(
            math.ceil(
                total / page_size
            )
            if total
            else 0
        ),
    )


@router.get(
    "/admin/subscriptions/summary",
    response_model=(
        AdminSubscriptionSummaryRead
    ),
)
def subscription_summary(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    total = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            )
        )
        or 0
    )

    free = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            ).where(
                OwnerSubscription.status
                == SubscriptionStatus.FREE
            )
        )
        or 0
    )

    active_paid = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            ).where(
                OwnerSubscription.status
                == SubscriptionStatus.ACTIVE
            )
        )
        or 0
    )

    incomplete = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            ).where(
                OwnerSubscription.status
                == SubscriptionStatus.INCOMPLETE
            )
        )
        or 0
    )

    past_due = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            ).where(
                OwnerSubscription.status
                == SubscriptionStatus.PAST_DUE
            )
        )
        or 0
    )

    canceled = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            ).where(
                OwnerSubscription.status
                == SubscriptionStatus.CANCELED
            )
        )
        or 0
    )

    return (
        AdminSubscriptionSummaryRead(
            total=total,
            free=free,
            active_paid=active_paid,
            incomplete=incomplete,
            past_due=past_due,
            canceled=canceled,
        )
    )


@router.get(
    "/admin/subscriptions",
    response_model=(
        AdminSubscriptionPage
    ),
)
def list_admin_subscriptions(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    search: str | None = None,
    subscription_status:
        SubscriptionStatus | None = None,
    plan_id: int | None = None,
):
    filters = [
        User.role
        == UserRole.OWNER
    ]

    if search:
        pattern = (
            f"%{search.strip()}%"
        )

        filters.append(
            or_(
                User.first_name.ilike(
                    pattern
                ),
                User.last_name.ilike(
                    pattern
                ),
                User.email.ilike(
                    pattern
                ),
            )
        )

    if (
        subscription_status
        is not None
    ):
        filters.append(
            OwnerSubscription.status
            == subscription_status
        )

    if plan_id is not None:
        filters.append(
            OwnerSubscription.plan_id
            == plan_id
        )

    total = (
        db.scalar(
            select(
                func.count(
                    OwnerSubscription.id
                )
            )
            .join(
                User,
                OwnerSubscription.owner_id
                == User.id,
            )
            .where(
                *filters
            )
        )
        or 0
    )

    property_count = (
        select(
            func.count(
                Property.id
            )
        )
        .where(
            Property.owner_id
            == User.id
        )
        .correlate(User)
        .scalar_subquery()
    )

    rows = db.execute(
        select(
            OwnerSubscription,
            SubscriptionPlan,
            User,
            property_count.label(
                "property_count"
            ),
        )
        .join(
            SubscriptionPlan,
            OwnerSubscription.plan_id
            == SubscriptionPlan.id,
        )
        .join(
            User,
            OwnerSubscription.owner_id
            == User.id,
        )
        .where(
            *filters
        )
        .order_by(
            OwnerSubscription
            .updated_at
            .desc(),
            OwnerSubscription.id.desc(),
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
    ).all()

    return AdminSubscriptionPage(
        items=[
            AdminSubscriptionItemRead(
                owner_id=owner.id,
                owner_email=owner.email,
                owner_first_name=(
                    owner.first_name
                ),
                owner_last_name=(
                    owner.last_name
                ),
                owner_is_active=(
                    owner.is_active
                ),
                plan_id=plan.id,
                plan_code=plan.code,
                plan_name=plan.name,
                status=(
                    subscription.status
                ),
                billing_interval=(
                    subscription
                    .billing_interval
                ),
                property_count=(
                    count
                    or 0
                ),
                max_properties=(
                    plan.max_properties
                ),
                current_period_end=(
                    subscription
                    .current_period_end
                ),
                cancel_at_period_end=(
                    subscription
                    .cancel_at_period_end
                ),
            )
            for (
                subscription,
                plan,
                owner,
                count,
            ) in rows
        ],
        meta=make_meta(
            page,
            page_size,
            total,
        ),
    )


@router.get(
    "/admin/subscription-payments",
    response_model=(
        AdminSubscriptionPaymentPage
    ),
)
def list_admin_subscription_payments(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    search: str | None = None,
    payment_status:
        SubscriptionPaymentStatus | None = None,
):
    filters = []

    if search:
        pattern = (
            f"%{search.strip()}%"
        )

        filters.append(
            or_(
                User.first_name.ilike(
                    pattern
                ),
                User.last_name.ilike(
                    pattern
                ),
                User.email.ilike(
                    pattern
                ),
                SubscriptionPayment
                .stripe_invoice_id
                .ilike(pattern),
            )
        )

    if payment_status is not None:
        filters.append(
            SubscriptionPayment.status
            == payment_status
        )

    total = (
        db.scalar(
            select(
                func.count(
                    SubscriptionPayment.id
                )
            )
            .join(
                User,
                SubscriptionPayment.owner_id
                == User.id,
            )
            .where(
                *filters
            )
        )
        or 0
    )

    rows = db.execute(
        select(
            SubscriptionPayment,
            SubscriptionPlan,
            User,
        )
        .join(
            SubscriptionPlan,
            SubscriptionPayment.plan_id
            == SubscriptionPlan.id,
        )
        .join(
            User,
            SubscriptionPayment.owner_id
            == User.id,
        )
        .where(
            *filters
        )
        .order_by(
            SubscriptionPayment
            .created_at
            .desc(),
            SubscriptionPayment.id
            .desc(),
        )
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
    ).all()

    return (
        AdminSubscriptionPaymentPage(
            items=[
                AdminSubscriptionPaymentItemRead(
                    id=payment.id,
                    owner_id=owner.id,
                    owner_email=owner.email,
                    owner_first_name=(
                        owner.first_name
                    ),
                    owner_last_name=(
                        owner.last_name
                    ),
                    plan_id=plan.id,
                    plan_code=plan.code,
                    plan_name=plan.name,
                    stripe_invoice_id=(
                        payment
                        .stripe_invoice_id
                    ),
                    amount=payment.amount,
                    currency=payment.currency,
                    status=payment.status,
                    created_at=(
                        payment.created_at
                    ),
                )
                for (
                    payment,
                    plan,
                    owner,
                ) in rows
            ],
            meta=make_meta(
                page,
                page_size,
                total,
            ),
        )
    )
