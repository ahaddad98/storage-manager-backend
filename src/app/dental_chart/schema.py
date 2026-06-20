from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DentalChartCreate(BaseModel):
    clinic_id: UUID
    patient_id: UUID
    notes: str | None = None
    status: str = Field(default="active", max_length=20)


class DentalChartUpdate(BaseModel):
    notes: str | None = None
    status: str | None = Field(None, max_length=20)


class DentalChartFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    status: str | None = None
    clinic_id: UUID | None = None


class ToothRecordCreate(BaseModel):
    tooth_number: int = Field(..., ge=1, le=52)
    status: str = Field(default="healthy", max_length=30)
    diagnosis: str | None = None
    notes: str | None = None
    planned_treatments: str | None = None
    completed_treatments: str | None = None


class ToothRecordUpdate(BaseModel):
    status: str | None = Field(None, max_length=30)
    diagnosis: str | None = None
    notes: str | None = None
    planned_treatments: str | None = None
    completed_treatments: str | None = None


class ToothRecordFilter(BaseModel):
    search: str | None = None
    tooth_number: int | None = None
    status: str | None = None
    chart_id: UUID | None = None


class ToothRecordResponse(BaseModel):
    id: UUID
    organization_id: UUID
    chart_id: UUID
    tooth_number: int
    status: str
    diagnosis: str | None
    notes: str | None
    planned_treatments: str | None
    completed_treatments: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class DentalChartResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    patient_id: UUID
    notes: str | None
    status: str
    teeth: list[ToothRecordResponse] = []
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
