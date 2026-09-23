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
    get_current_user,
)
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import (
    OwnerRegister,
    UserRead,
)
from app.services.subscriptions import (
    assign_free_plan,
)


router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def register_owner(
    payload: OwnerRegister,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:
    normalized_email = (
        payload.email.lower()
    )

    existing_user = db.scalar(
        select(User).where(
            User.email
            == normalized_email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "An account with this "
                "email already exists."
            ),
        )

    user = User(
        email=normalized_email,
        password_hash=(
            hash_password(
                payload.password
            )
        ),
        role=UserRole.OWNER,
    )

    db.add(user)
    db.flush()

    assign_free_plan(
        db,
        user.id,
    )

    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> TokenResponse:
    normalized_email = (
        payload.email.lower()
    )

    user = db.scalar(
        select(User).where(
            User.email
            == normalized_email
        )
    )

    if user is None:
        verify_password(
            payload.password,
            DUMMY_PASSWORD_HASH,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid email or password."
            ),
        )

    if not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid email or password."
            ),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Account is disabled."
            ),
        )

    access_token = (
        create_access_token(
            user.id
        )
    )

    return TokenResponse(
        access_token=(
            access_token
        ),
    )


@router.get(
    "/me",
    response_model=UserRead,
)
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    return current_user
