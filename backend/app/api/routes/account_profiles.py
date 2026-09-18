from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    require_owner,
)
from app.core.security import (
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.workflow import (
    OwnerTenantCreate,
    PasswordChange,
    UserProfileUpdate,
    UserSummary,
)


router = APIRouter()


@router.get(
    "/auth/me/profile",
    response_model=UserSummary,
)
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return current_user


@router.patch(
    "/auth/me/profile",
    response_model=UserSummary,
)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    changes = payload.model_dump(
        exclude_unset=True,
    )

    if "email" in changes:
        new_email = str(
            changes["email"]
        ).strip().lower()

        existing = db.scalar(
            select(User).where(
                User.email
                == new_email,
                User.id
                != current_user.id,
            )
        )

        if existing is not None:
            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail=(
                    "Another account already "
                    "uses this email."
                ),
            )

        changes["email"] = (
            new_email
        )

    for (
        field,
        value,
    ) in changes.items():
        setattr(
            current_user,
            field,
            value,
        )

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch(
    "/auth/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_my_password(
    payload: PasswordChange,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    if not verify_password(
        payload.current_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Current password is incorrect."
            ),
        )

    current_user.password_hash = (
        hash_password(
            payload.new_password
        )
    )

    db.commit()

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )


@router.post(
    "/owner/tenants",
    response_model=UserSummary,
    status_code=status.HTTP_201_CREATED,
)
def create_detailed_tenant(
    payload: OwnerTenantCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    normalized_email = str(
        payload.email
    ).strip().lower()

    existing = db.scalar(
        select(User).where(
            User.email
            == normalized_email
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A user with this email "
                "already exists."
            ),
        )

    tenant = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_number=(
            payload.phone_number
        ),
        email=normalized_email,
        password_hash=hash_password(
            payload.password
        ),
        role=UserRole.TENANT,
        is_active=True,
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant


@router.get(
    "/owner/tenants/lookup",
    response_model=UserSummary,
)
def lookup_tenant_by_email(
    email: Annotated[
        str,
        Query(
            min_length=3,
            max_length=255,
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_owner: Annotated[
        User,
        Depends(require_owner),
    ],
):
    normalized_email = (
        email.strip().lower()
    )

    tenant = db.scalar(
        select(User).where(
            User.email
            == normalized_email,
            User.role
            == UserRole.TENANT,
            User.is_active.is_(True),
        )
    )

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No active tenant account "
                "was found with this email."
            ),
        )

    return tenant