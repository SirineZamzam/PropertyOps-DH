from calendar import monthrange
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lease import Lease
from app.models.payment import (
    Payment,
    PaymentStatus,
)
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)


def add_calendar_months(
    anchor: date,
    months: int,
) -> date:
    month_index = (
        anchor.month - 1 + months
    )

    year = (
        anchor.year
        + month_index // 12
    )

    month = (
        month_index % 12
        + 1
    )

    last_day = monthrange(
        year,
        month,
    )[1]

    day = min(
        anchor.day,
        last_day,
    )

    return date(
        year,
        month,
        day,
    )


def calendar_month_count(
    start_date: date,
    end_date: date,
) -> int:
    if end_date <= start_date:
        raise ValueError(
            "Lease end date must be after the start date."
        )

    months = (
        (end_date.year - start_date.year) * 12
        + end_date.month
        - start_date.month
    )

    if (
        months <= 0
        or add_calendar_months(
            start_date,
            months,
        )
        != end_date
    ):
        raise ValueError(
            "Lease end date must fall on a full calendar-month "
            "boundary from the start date."
        )

    return months


def validate_lease_term(
    start_date: date,
    end_date: date | None,
) -> None:
    if end_date is None:
        return

    calendar_month_count(
        start_date,
        end_date,
    )


def monthly_due_dates(
    start_date: date,
    end_date: date | None,
) -> list[date]:
    if end_date is None:
        # Existing/open-ended leases remain supported.
        # Without a known term we create the first obligation only;
        # the normal UI now asks for an end date so full schedules
        # can be generated deterministically.
        return [
            start_date,
        ]

    months = calendar_month_count(
        start_date,
        end_date,
    )

    return [
        add_calendar_months(
            start_date,
            offset,
        )
        for offset in range(
            months
        )
    ]


def generate_initial_rent_schedule(
    db: Session,
    lease: Lease,
) -> None:
    for due_date in monthly_due_dates(
        lease.start_date,
        lease.end_date,
    ):
        db.add(
            RentObligation(
                lease_id=lease.id,
                amount=(
                    lease.rent_amount
                ),
                due_date=due_date,
                status=(
                    RentObligationStatus.PENDING
                ),
            )
        )


def expire_open_payment_attempts(
    db: Session,
    obligation_ids: list[int],
) -> None:
    if not obligation_ids:
        return

    payments = db.scalars(
        select(Payment).where(
            Payment.rent_obligation_id.in_(
                obligation_ids
            ),
            Payment.status.in_(
                [
                    PaymentStatus.PENDING,
                    PaymentStatus.PROCESSING,
                ]
            ),
        )
    ).all()

    for payment in payments:
        payment.status = (
            PaymentStatus.EXPIRED
        )


def reconcile_active_lease_schedule(
    db: Session,
    lease: Lease,
    *,
    today: date | None = None,
) -> None:
    current_date = (
        today
        or date.today()
    )

    desired_dates = set(
        monthly_due_dates(
            lease.start_date,
            lease.end_date,
        )
    )

    obligations = list(
        db.scalars(
            select(
                RentObligation
            )
            .where(
                RentObligation.lease_id
                == lease.id
            )
            .order_by(
                RentObligation.due_date
            )
        ).all()
    )

    by_due_date = {
        obligation.due_date:
            obligation
        for obligation
        in obligations
    }

    canceled_ids: list[int] = []

    for obligation in obligations:
        if (
            obligation.due_date
            < current_date
        ):
            # Historical obligations are never rewritten.
            continue

        if (
            lease.end_date
            is not None
            and (
                obligation.due_date
                < lease.start_date
                or obligation.due_date
                >= lease.end_date
            )
        ):
            if (
                obligation.status
                == RentObligationStatus.PENDING
            ):
                obligation.status = (
                    RentObligationStatus.CANCELED
                )

                canceled_ids.append(
                    obligation.id
                )

            continue

        if (
            obligation.due_date
            in desired_dates
        ):
            if (
                obligation.status
                == RentObligationStatus.CANCELED
            ):
                obligation.status = (
                    RentObligationStatus.PENDING
                )

            if (
                obligation.status
                == RentObligationStatus.PENDING
            ):
                obligation.amount = (
                    lease.rent_amount
                )

    expire_open_payment_attempts(
        db,
        canceled_ids,
    )

    for due_date in sorted(
        desired_dates
    ):
        if due_date < current_date:
            continue

        existing = by_due_date.get(
            due_date
        )

        if existing is not None:
            continue

        db.add(
            RentObligation(
                lease_id=lease.id,
                amount=(
                    lease.rent_amount
                ),
                due_date=due_date,
                status=(
                    RentObligationStatus.PENDING
                ),
            )
        )


def cancel_future_obligations(
    db: Session,
    lease: Lease,
    *,
    cutoff: date,
) -> None:
    obligations = list(
        db.scalars(
            select(
                RentObligation
            ).where(
                RentObligation.lease_id
                == lease.id,
                RentObligation.status
                == RentObligationStatus.PENDING,
                RentObligation.due_date
                >= cutoff,
            )
        ).all()
    )

    obligation_ids: list[int] = []

    for obligation in obligations:
        obligation.status = (
            RentObligationStatus.CANCELED
        )

        obligation_ids.append(
            obligation.id
        )

    expire_open_payment_attempts(
        db,
        obligation_ids,
    )
