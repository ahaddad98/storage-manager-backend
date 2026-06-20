from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    clinic_id: UUID
    patient_id: UUID
    dentist_id: UUID | None = None
    room_id: UUID | None = None
    start_time: datetime
    end_time: datetime
    treatment_type: str | None = Field(None, max_length=255)
    notes: str | None = None
    status: str = Field(default="scheduled", max_length=30)
    reminder_status: str = Field(default="pending", max_length=30)


class AppointmentUpdate(BaseModel):
    dentist_id: UUID | None = None
    room_id: UUID | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    treatment_type: str | None = Field(None, max_length=255)
    notes: str | None = None
    status: str | None = Field(None, max_length=30)
    reminder_status: str | None = Field(None, max_length=30)


class AppointmentFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    dentist_id: UUID | None = None
    room_id: UUID | None = None
    status: str | None = None
    clinic_id: UUID | None = None
    start_from: datetime | None = None
    start_to: datetime | None = None


class AppointmentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    created_by: UUID | None
    patient_id: UUID
    dentist_id: UUID | None
    room_id: UUID | None
    start_time: datetime
    end_time: datetime
    treatment_type: str | None
    notes: str | None
    status: str
    reminder_status: str
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
