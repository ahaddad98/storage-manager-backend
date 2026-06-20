from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    clinic_id: UUID
    patient_id: UUID | None = None
    treatment_id: UUID | None = None
    invoice_id: UUID | None = None
    file_name: str = Field(..., max_length=255)
    file_type: str | None = Field(None, max_length=50)
    document_type: str = Field(default="other", max_length=50)
    file_url: str | None = None
    notes: str | None = None


class DocumentUpdate(BaseModel):
    patient_id: UUID | None = None
    treatment_id: UUID | None = None
    invoice_id: UUID | None = None
    file_name: str | None = Field(None, max_length=255)
    file_type: str | None = Field(None, max_length=50)
    document_type: str | None = Field(None, max_length=50)
    file_url: str | None = None
    notes: str | None = None


class DocumentFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    treatment_id: UUID | None = None
    invoice_id: UUID | None = None
    document_type: str | None = None
    clinic_id: UUID | None = None


class ActivityLogFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    clinic_id: UUID | None = None
    user_id: UUID | None = None
    event_type: str | None = None


class DocumentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    created_by: UUID | None
    patient_id: UUID | None
    treatment_id: UUID | None
    invoice_id: UUID | None
    file_name: str
    file_type: str | None
    document_type: str
    file_url: str | None
    notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class ActivityLogResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID | None
    patient_id: UUID | None
    user_id: UUID | None
    event_type: str
    description: str
    entity_type: str | None
    entity_id: UUID | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
