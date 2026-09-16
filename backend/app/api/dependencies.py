from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
    )

    if credentials is None:
        raise credentials_error

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_error

        user_id = int(subject)

    except (InvalidTokenError, ValueError):
        raise credentials_error

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_error

    return user


def require_owner(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required.",
        )

    return current_user

def require_tenant(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    if current_user.role != UserRole.TENANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access required.",
        )

    return current_user