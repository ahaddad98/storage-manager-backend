from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.staff.model import Membership
from core.config import get_settings
from core.database.session import get_db_session
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.role_list import ROLE_PERMISSIONS

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(
    subject: str | UUID, role: str = "user", extra: dict[str, Any] | None = None
) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    return payload


def require_permission(permission: str):
    async def permission_checker(
        user: dict[str, Any] = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> dict[str, Any]:
        organization_id = user.get("organization_id")
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No organization context",
            )
        membership_result = await session.execute(
            select(Membership).where(
                Membership.user_id == UUID(user["sub"]),
                Membership.organization_id == UUID(organization_id),
                Membership.status == "active",
            )
        )
        membership = membership_result.scalar_one_or_none()
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active organization membership",
            )
        role = membership.role
        permissions = ROLE_PERMISSIONS.get(role, set())
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        user["role"] = role
        return user

    return permission_checker


def require_any_permission(permissions_to_check: list[str]):
    async def permission_checker(
        user: dict[str, Any] = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> dict[str, Any]:
        organization_id = user.get("organization_id")
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No organization context",
            )
        membership_result = await session.execute(
            select(Membership).where(
                Membership.user_id == UUID(user["sub"]),
                Membership.organization_id == UUID(organization_id),
                Membership.status == "active",
            )
        )
        membership = membership_result.scalar_one_or_none()
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active organization membership",
            )

        role_permissions = ROLE_PERMISSIONS.get(membership.role, set())
        if not any(permission in role_permissions for permission in permissions_to_check):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of {permissions_to_check!r} required",
            )
        user["role"] = membership.role
        return user

    return permission_checker
