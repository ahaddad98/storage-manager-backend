from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    organization_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: str | None
    is_active: bool
    last_active: datetime | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class MembershipInfo(BaseModel):
    organization_id: UUID
    organization_name: str
    role: str
    status: str
    business_type: str = "dental_clinic"
    enabled_modules: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class AuthMeResponse(BaseModel):
    user: UserResponse
    membership: MembershipInfo
    clinic_ids: list[UUID]


class InviteStaffRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(default="assistant")
    clinic_ids: list[UUID] = Field(default_factory=list)


class AcceptInvitationRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
