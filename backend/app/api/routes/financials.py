from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)
from decimal import Decimal
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.building import Building
from app.models.expense import Expense
from app.models.lease import Lease
from app.models.payment import (
    Payment,
    PaymentStatus,
)
from app.models.property import Property
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
from app.models.unit import Unit
from app.models.user import User
from app.schemas.finance import (
    FinancialOverviewRead,
    FinancialSeriesPoint,
)


router = APIRouter()


def month_key(
    value: date,
) -> str:
    return (
        f"{value.year:04d}-"
        f"{value.month:02d}"
    )


def month_sequence(
    start: date,
    end: date,
) -> list[str]:
    current_year = start.year
    current_month = start.month

    keys: list[str] = []

    while (
        current_year < end.year
        or (
            current_year == end.year
            and current_month <= end.month
        )
    ):
        keys.append(
            f"{current_year:04d}-"
            f"{current_month:02d}"
        )

        current_month += 1

        if current_month == 13:
            current_month = 1
            current_year += 1

    return keys


@router.get(
    "/owner/financial-overview",
    response_model=FinancialOverviewRead,
)
def owner_financial_overview(
    start_date: Annotated[
        date,
        Query(),
    ],
    end_date: Annotated[
        date,
        Query(),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "End date must be on or after start date."
            ),
        )

    day_count = (
        end_date - start_date
    ).days + 1

    if day_count > 730:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Financial overview range cannot exceed 730 days."
            ),
        )

    start_dt = datetime.combine(
        start_date,
        time.min,
        tzinfo=timezone.utc,
    )

    end_dt = datetime.combine(
        end_date + timedelta(days=1),
        time.min,
        tzinfo=timezone.utc,
    )

    payment_rows = db.execute(
        select(
            Payment.amount,
            Payment.paid_at,
        )
        .join(
            RentObligation,
            Payment.rent_obligation_id
            == RentObligation.id,
        )
        .join(
            Lease,
            RentObligation.lease_id
            == Lease.id,
        )
        .join(
            Unit,
            Lease.unit_id
            == Unit.id,
        )
        .join(
            Building,
            Unit.building_id
            == Building.id,
        )
        .join(
            Property,
            Building.property_id
            == Property.id,
        )
        .where(
            Property.owner_id == owner.id,
            Payment.status == PaymentStatus.PAID,
            Payment.paid_at.is_not(None),
            Payment.paid_at >= start_dt,
            Payment.paid_at < end_dt,
        )
    ).all()

    expense_rows = db.execute(
        select(
            Expense.amount,
            Expense.expense_date,
        ).where(
            Expense.owner_id == owner.id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        )
    ).all()

    outstanding_rent = (
        db.scalar(
            select(
                func.coalesce(
                    func.sum(
                        RentObligation.amount
                    ),
                    0,
                )
            )
            .join(
                Lease,
                RentObligation.lease_id
                == Lease.id,
            )
            .join(
                Unit,
                Lease.unit_id
                == Unit.id,
            )
            .join(
                Building,
                Unit.building_id
                == Building.id,
            )
            .join(
                Property,
                Building.property_id
                == Property.id,
            )
            .where(
                Property.owner_id == owner.id,
                RentObligation.status
                == RentObligationStatus.PENDING,
                RentObligation.due_date >= start_date,
                RentObligation.due_date <= end_date,
            )
        )
        or Decimal("0")
    )

    rent_collected = sum(
        (
            row.amount
            for row in payment_rows
        ),
        Decimal("0"),
    )

    expenses_total = sum(
        (
            row.amount
            for row in expense_rows
        ),
        Decimal("0"),
    )

    net_cash_flow = (
        rent_collected
        - expenses_total
    )

    bucket = (
        "DAY"
        if day_count <= 62
        else "MONTH"
    )

    series_map: dict[
        str,
        dict[str, Decimal],
    ] = {}

    if bucket == "DAY":
        current = start_date

        while current <= end_date:
            series_map[
                current.isoformat()
            ] = {
                "rent_collected":
                    Decimal("0"),
                "expenses":
                    Decimal("0"),
            }

            current += timedelta(
                days=1
            )

    else:
        for key in month_sequence(
            start_date,
            end_date,
        ):
            series_map[key] = {
                "rent_collected":
                    Decimal("0"),
                "expenses":
                    Decimal("0"),
            }

    for row in payment_rows:
        if row.paid_at is None:
            continue

        paid_date = (
            row.paid_at.date()
        )

        key = (
            paid_date.isoformat()
            if bucket == "DAY"
            else month_key(
                paid_date
            )
        )

        if key in series_map:
            series_map[key][
                "rent_collected"
            ] += row.amount

    for row in expense_rows:
        key = (
            row.expense_date.isoformat()
            if bucket == "DAY"
            else month_key(
                row.expense_date
            )
        )

        if key in series_map:
            series_map[key][
                "expenses"
            ] += row.amount

    series = [
        FinancialSeriesPoint(
            label=label,
            rent_collected=(
                values[
                    "rent_collected"
                ]
            ),
            expenses=(
                values[
                    "expenses"
                ]
            ),
        )
        for (
            label,
            values,
        ) in series_map.items()
    ]

    return FinancialOverviewRead(
        start_date=start_date,
        end_date=end_date,
        bucket=bucket,
        rent_collected=rent_collected,
        expenses=expenses_total,
        net_cash_flow=net_cash_flow,
        outstanding_rent=outstanding_rent,
        series=series,
    )
