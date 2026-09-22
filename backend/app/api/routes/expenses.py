from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.db.session import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseRead,
    GeneralExpenseCreate,
)
from app.services.ownership import (
    get_owned_property,
    get_owned_unit,
)


router = APIRouter()


@router.post(
    "/properties/{property_id}/expenses",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    property_id: int,
    payload: ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Expense:
    get_owned_property(
        db,
        current_owner.id,
        property_id,
    )

    if payload.unit_id is not None:
        unit = get_owned_unit(
            db,
            current_owner.id,
            payload.unit_id,
        )

        if (
            unit.building.property_id
            != property_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit does not belong to this property.",
            )

    expense = Expense(
        owner_id=current_owner.id,
        property_id=property_id,
        unit_id=payload.unit_id,
        amount=payload.amount,
        category=payload.category.strip(),
        expense_date=payload.expense_date,
        description=(
            payload.description.strip()
            if payload.description
            else None
        ),
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.post(
    "/owner/expenses/general",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_general_expense(
    payload: GeneralExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> Expense:
    expense = Expense(
        owner_id=current_owner.id,
        property_id=None,
        unit_id=None,
        maintenance_id=None,
        amount=payload.amount,
        category=payload.category.strip(),
        expense_date=payload.expense_date,
        description=(
            payload.description.strip()
            if payload.description
            else None
        ),
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get(
    "/properties/{property_id}/expenses",
    response_model=list[ExpenseRead],
)
def list_property_expenses(
    property_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
) -> list[Expense]:
    get_owned_property(
        db,
        current_owner.id,
        property_id,
    )

    statement = (
        select(Expense)
        .where(
            Expense.owner_id == current_owner.id,
            Expense.property_id == property_id,
        )
        .order_by(
            Expense.expense_date.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )
