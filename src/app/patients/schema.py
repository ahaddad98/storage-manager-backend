from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    clinic_id: UUID
    full_name: str = Field(..., max_length=255)
    birth_date: date | None = None
    gender: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    address: str | None = None
    emergency_contact: str | None = None
    occupation: str | None = Field(None, max_length=100)
    status: str = Field(default="active", max_length=20)
    notes: str | None = None


class PatientUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=255)
    birth_date: date | None = None
    gender: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    address: str | None = None
    emergency_contact: str | None = None
    occupation: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=20)
    notes: str | None = None


class PatientFilter(BaseModel):
    search: str | None = None
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None
    clinic_id: UUID | None = None


class PatientResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    created_by: UUID | None
    full_name: str
    birth_date: date | None
    gender: str | None
    phone: str | None
    email: str | None
    address: str | None
    emergency_contact: str | None
    occupation: str | None
    status: str
    notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class MedicalHistoryUpdate(BaseModel):
    allergies: str | None = None
    chronic_diseases: str | None = None
    current_medications: str | None = None
    pregnancy_status: str | None = Field(None, max_length=50)
    smoking_status: str | None = Field(None, max_length=50)
    previous_surgeries: str | None = None
    medical_alerts: str | None = None
    blood_pressure_notes: str | None = None
    doctor_notes: str | None = None


class MedicalHistoryResponse(BaseModel):
    id: UUID
    organization_id: UUID
    patient_id: UUID
    allergies: str | None
    chronic_diseases: str | None
    current_medications: str | None
    pregnancy_status: str | None
    smoking_status: str | None
    previous_surgeries: str | None
    medical_alerts: str | None
    blood_pressure_notes: str | None
    doctor_notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
