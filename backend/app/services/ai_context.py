from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy import (
    or_,
    select,
)

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.building import Building
from app.models.expense import Expense
from app.models.maintenance import Maintenance
from app.models.property import Property
from app.models.unit import Unit

from app.services.ownership import (
    get_owned_property,
    get_owned_unit,
)


def _maintenance_payload(
    record: Maintenance,
    *,
    unit_number: str,
    building_name: str,
) -> dict:
    return {
        "id": record.id,

        "unit_id":
            record.unit_id,

        "unit_number":
            unit_number,

        "building_name":
            building_name,

        "category":
            record.category,

        "description":
            record.description,

        "status":
            record.status.value,

        "created_at": (
            record
            .created_at
            .isoformat()
        ),

        "resolved_at": (
            record.resolved_at.isoformat()
            if record.resolved_at
            else None
        ),
    }


def _expense_payload(
    record: Expense,
    *,
    unit_number:
        str | None,

    building_name:
        str | None,
) -> dict:
    return {
        "id":
            record.id,

        "property_id":
            record.property_id,

        "unit_id":
            record.unit_id,

        "unit_number":
            unit_number,

        "building_name":
            building_name,

        "maintenance_id":
            record.maintenance_id,

        "amount":
            str(record.amount),

        "category":
            record.category,

        "description":
            record.description,

        "expense_date": (
            record
            .expense_date
            .isoformat()
        ),
    }


def _analysis_window() -> tuple[
    datetime,
    datetime,
]:
    window_end = datetime.now(
        timezone.utc
    )

    window_start = (
        window_end
        - timedelta(
            days=(
                settings
                .ai_lookback_days
            )
        )
    )

    return (
        window_start,
        window_end,
    )


# --------------------------------------------------
# PROPERTY CONTEXT
# --------------------------------------------------

def collect_property_ai_context(
    db: Session,
    *,
    owner_id: int,
    property_id: int,
) -> dict:
    property_record = (
        get_owned_property(
            db,
            owner_id,
            property_id,
        )
    )

    limit = (
        settings
        .ai_max_records_per_type
    )

    (
        window_start,
        window_end,
    ) = _analysis_window()

    # ----------------------------------------------
    # Maintenance
    # ----------------------------------------------

    maintenance_rows = (
        db.execute(
            select(
                Maintenance,
                Unit.unit_number,
                Building.name,
            )
            .join(
                Unit,
                Maintenance.unit_id
                == Unit.id,
            )
            .join(
                Building,
                Unit.building_id
                == Building.id,
            )
            .where(
                Building.property_id
                == property_record.id,

                Maintenance.created_at
                >= window_start,
            )
            .order_by(
                Maintenance
                .created_at
                .desc()
            )
            .limit(limit)
        )
        .all()
    )

    # ----------------------------------------------
    # Expenses
    # ----------------------------------------------

    expense_rows = (
        db.execute(
            select(
                Expense,
                Unit.unit_number,
                Building.name,
            )
            .outerjoin(
                Unit,
                Expense.unit_id
                == Unit.id,
            )
            .outerjoin(
                Building,
                Unit.building_id
                == Building.id,
            )
            .where(
                Expense.property_id
                == property_record.id,

                Expense.expense_date
                >= window_start.date(),
            )
            .order_by(
                Expense
                .expense_date
                .desc()
            )
            .limit(limit)
        )
        .all()
    )

    # ----------------------------------------------
    # Payloads
    # ----------------------------------------------

    maintenance = [
        _maintenance_payload(
            record,
            unit_number=unit_number,
            building_name=(
                building_name
            ),
        )
        for (
            record,
            unit_number,
            building_name,
        )
        in maintenance_rows
    ]

    expenses = [
        _expense_payload(
            record,
            unit_number=unit_number,
            building_name=(
                building_name
            ),
        )
        for (
            record,
            unit_number,
            building_name,
        )
        in expense_rows
    ]

    return {
        "scope": {
            "type":
                "PROPERTY",

            "property_id":
                property_record.id,

            "property_name":
                property_record.name,

            "city":
                property_record.city,

            "country":
                property_record.country,

            "analysis_window_days":
                settings.ai_lookback_days,

            "analysis_window_start":
                window_start.isoformat(),

            "analysis_window_end":
                window_end.isoformat(),
        },

        "maintenance":
            maintenance,

        "expenses":
            expenses,
    }


# --------------------------------------------------
# UNIT CONTEXT
# --------------------------------------------------

def collect_unit_ai_context(
    db: Session,
    *,
    owner_id: int,
    unit_id: int,
) -> dict:
    unit = get_owned_unit(
        db,
        owner_id,
        unit_id,
    )

    building = unit.building

    property_record = (
        building.property
    )

    limit = (
        settings
        .ai_max_records_per_type
    )

    (
        window_start,
        window_end,
    ) = _analysis_window()

    # ----------------------------------------------
    # Maintenance
    # ----------------------------------------------

    maintenance_records = (
        db.scalars(
            select(
                Maintenance
            )
            .where(
                Maintenance.unit_id
                == unit.id,

                Maintenance.created_at
                >= window_start,
            )
            .order_by(
                Maintenance
                .created_at
                .desc()
            )
            .limit(limit)
        )
        .all()
    )

    # Used so expenses linked indirectly
    # through maintenance can still be
    # associated with this unit.
    maintenance_id_query = (
        select(
            Maintenance.id
        )
        .where(
            Maintenance.unit_id
            == unit.id
        )
    )

    # ----------------------------------------------
    # Expenses
    # ----------------------------------------------

    expense_records = (
        db.scalars(
            select(
                Expense
            )
            .where(
                Expense.property_id
                == property_record.id,

                Expense.expense_date
                >= window_start.date(),

                or_(
                    Expense.unit_id
                    == unit.id,

                    Expense
                    .maintenance_id
                    .in_(
                        maintenance_id_query
                    ),
                ),
            )
            .order_by(
                Expense
                .expense_date
                .desc()
            )
            .limit(limit)
        )
        .all()
    )

    # ----------------------------------------------
    # Payloads
    # ----------------------------------------------

    maintenance = [
        _maintenance_payload(
            record,

            unit_number=(
                unit.unit_number
            ),

            building_name=(
                building.name
            ),
        )
        for record
        in maintenance_records
    ]

    expenses = [
        _expense_payload(
            record,

            unit_number=(
                unit.unit_number
            ),

            building_name=(
                building.name
            ),
        )
        for record
        in expense_records
    ]

    return {
        "scope": {
            "type":
                "UNIT",

            "property_id":
                property_record.id,

            "property_name":
                property_record.name,

            "building_id":
                building.id,

            "building_name":
                building.name,

            "unit_id":
                unit.id,

            "unit_number":
                unit.unit_number,

            "unit_type":
                unit.unit_type.value,

            "analysis_window_days":
                settings.ai_lookback_days,

            "analysis_window_start":
                window_start.isoformat(),

            "analysis_window_end":
                window_end.isoformat(),
        },

        "maintenance":
            maintenance,

        "expenses":
            expenses,
    }