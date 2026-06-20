from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import (
    AcceptInvitationRequest,
    AuthMeResponse,
    InviteStaffRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService
from core.database.session import get_db_session
from core.middleware.auth.exceptions import get_current_user, require_permission
from core.middleware.auth.permission_list import Permission

router = APIRouter()


def get_auth_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> AuthService:
    return AuthService(session)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.login(data)


@router.get("/me", response_model=AuthMeResponse)
async def get_me(
    user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthMeResponse:
    return await service.get_me(
        user_id=UUID(user["sub"]),
        organization_id=UUID(user["organization_id"]),
    )


@router.post("/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_staff(
    data: InviteStaffRequest,
    current_user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    return await service.invite_staff(data, UUID(current_user["organization_id"]))


@router.post("/accept-invitation", response_model=TokenResponse)
async def accept_invitation(
    data: AcceptInvitationRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.accept_invitation(data)
