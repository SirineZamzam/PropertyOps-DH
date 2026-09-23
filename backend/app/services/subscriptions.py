from decimal import Decimal

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.owner_subscription import (
    OwnerSubscription,
    SubscriptionStatus,
)
from app.models.property import Property
from app.models.subscription_plan import (
    SubscriptionPlan,
)


DEFAULT_PLANS = (
    {
        "code": "FREE",
        "name": "Free",
        "monthly_price":
            Decimal("0.00"),
        "yearly_price":
            Decimal("0.00"),
        "max_properties": 2,
        "sort_order": 10,
    },
    {
        "code": "STANDARD",
        "name": "Standard",
        "monthly_price":
            Decimal("9.00"),
        "yearly_price":
            Decimal("90.00"),
        "max_properties": 10,
        "sort_order": 20,
    },
    {
        "code": "PRO",
        "name": "Pro",
        "monthly_price":
            Decimal("19.00"),
        "yearly_price":
            Decimal("190.00"),
        "max_properties": None,
        "sort_order": 30,
    },
)


def ensure_default_plans(
    db: Session,
) -> None:
    existing_codes = set(
        db.scalars(
            select(
                SubscriptionPlan.code
            ).where(
                SubscriptionPlan.code.in_(
                    [
                        plan["code"]
                        for plan
                        in DEFAULT_PLANS
                    ]
                )
            )
        ).all()
    )

    for plan_data in DEFAULT_PLANS:
        if (
            plan_data["code"]
            in existing_codes
        ):
            continue

        db.add(
            SubscriptionPlan(
                **plan_data,
                is_active=True,
            )
        )

    db.flush()


def get_plan_by_code(
    db: Session,
    code: str,
) -> SubscriptionPlan:
    plan = db.scalar(
        select(
            SubscriptionPlan
        ).where(
            SubscriptionPlan.code
            == code.upper()
        )
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


def assign_free_plan(
    db: Session,
    owner_id: int,
) -> OwnerSubscription:
    existing = db.scalar(
        select(
            OwnerSubscription
        ).where(
            OwnerSubscription.owner_id
            == owner_id
        )
    )

    if existing is not None:
        return existing

    ensure_default_plans(db)

    free_plan = get_plan_by_code(
        db,
        "FREE",
    )

    subscription = (
        OwnerSubscription(
            owner_id=owner_id,
            plan_id=free_plan.id,
            status=(
                SubscriptionStatus.FREE
            ),
        )
    )

    db.add(subscription)
    db.flush()

    return subscription


def get_owner_subscription(
    db: Session,
    owner_id: int,
) -> tuple[
    OwnerSubscription,
    SubscriptionPlan,
]:
    row = db.execute(
        select(
            OwnerSubscription,
            SubscriptionPlan,
        )
        .join(
            SubscriptionPlan,
            OwnerSubscription.plan_id
            == SubscriptionPlan.id,
        )
        .where(
            OwnerSubscription.owner_id
            == owner_id
        )
    ).first()

    if row is None:
        subscription = (
            assign_free_plan(
                db,
                owner_id,
            )
        )

        plan = db.get(
            SubscriptionPlan,
            subscription.plan_id,
        )

        if plan is None:
            raise RuntimeError(
                "Default FREE plan "
                "could not be loaded."
            )

        return (
            subscription,
            plan,
        )

    return (
        row[0],
        row[1],
    )


def property_count_for_owner(
    db: Session,
    owner_id: int,
) -> int:
    return (
        db.scalar(
            select(
                func.count(
                    Property.id
                )
            ).where(
                Property.owner_id
                == owner_id
            )
        )
        or 0
    )


def enforce_property_limit(
    db: Session,
    owner_id: int,
) -> None:
    (
        _,
        plan,
    ) = get_owner_subscription(
        db,
        owner_id,
    )

    if (
        plan.max_properties
        is None
    ):
        return

    current_count = (
        property_count_for_owner(
            db,
            owner_id,
        )
    )

    if (
        current_count
        >= plan.max_properties
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Property limit reached "
                f"for the {plan.name} "
                f"plan ({plan.max_properties} "
                "properties). Upgrade your "
                "plan to add more properties."
            ),
        )
