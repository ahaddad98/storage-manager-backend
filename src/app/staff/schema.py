from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MembershipFilter(BaseModel):
    search: str | None = None
    role: str | None = None
    status: str | None = None


class MembershipUpdate(BaseModel):
    role: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=20)


class ClinicAssignmentCreate(BaseModel):
    clinic_id: UUID


class ClinicAssignmentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    membership_id: UUID
    clinic_id: UUID
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class StaffUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class MembershipResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    invited_at: datetime | None
    joined_at: datetime | None
    user: StaffUserResponse | None = None
    clinic_assignments: list[ClinicAssignmentResponse] = []
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
