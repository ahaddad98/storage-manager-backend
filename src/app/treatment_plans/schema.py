from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TreatmentPlanCreate(BaseModel):
    clinic_id: UUID
    patient_id: UUID
    dentist_id: UUID | None = None
    title: str = Field(..., max_length=255)
    description: str | None = None
    status: str = Field(default="draft", max_length=30)
    estimated_total: Decimal = Field(default=Decimal("0"))
    notes: str | None = None


class TreatmentPlanUpdate(BaseModel):
    dentist_id: UUID | None = None
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: str | None = Field(None, max_length=30)
    estimated_total: Decimal | None = None
    notes: str | None = None


class TreatmentPlanFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    dentist_id: UUID | None = None
    status: str | None = None
    clinic_id: UUID | None = None


class TreatmentItemCreate(BaseModel):
    tooth_number: int | None = None
    name: str = Field(..., max_length=255)
    description: str | None = None
    estimated_cost: Decimal = Field(default=Decimal("0"))
    status: str = Field(default="planned", max_length=30)
    priority: str = Field(default="normal", max_length=20)
    notes: str | None = None


class TreatmentItemUpdate(BaseModel):
    tooth_number: int | None = None
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    estimated_cost: Decimal | None = None
    status: str | None = Field(None, max_length=30)
    priority: str | None = Field(None, max_length=20)
    notes: str | None = None


class TreatmentItemFilter(BaseModel):
    search: str | None = None
    status: str | None = None
    priority: str | None = None
    plan_id: UUID | None = None


class TreatmentItemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    plan_id: UUID
    tooth_number: int | None
    name: str
    description: str | None
    estimated_cost: Decimal
    status: str
    priority: str
    notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class TreatmentPlanResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    created_by: UUID | None
    patient_id: UUID
    dentist_id: UUID | None
    title: str
    description: str | None
    status: str
    estimated_total: Decimal
    notes: str | None
    items: list[TreatmentItemResponse] = []
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
