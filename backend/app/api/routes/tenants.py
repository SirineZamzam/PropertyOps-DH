from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserRead


router = APIRouter()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    payload: TenantCreate,
    db: Annotated[Session, Depends(get_db)],
    current_owner: Annotated[User, Depends(require_owner)],
) -> User:
    normalized_email = payload.email.lower()

    existing_user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    tenant = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role=UserRole.TENANT,
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant