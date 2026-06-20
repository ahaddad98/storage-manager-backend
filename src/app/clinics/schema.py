from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ClinicCreate(BaseModel):
    name: str = Field(..., max_length=255)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    logo_url: str | None = None
    opening_hours: dict | None = None
    timezone: str = Field(default="UTC", max_length=50)
    notes: str | None = None
    status: str = Field(default="active", max_length=20)


class ClinicUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    logo_url: str | None = None
    opening_hours: dict | None = None
    timezone: str | None = Field(None, max_length=50)
    notes: str | None = None
    status: str | None = Field(None, max_length=20)


class ClinicFilter(BaseModel):
    search: str | None = None
    name: str | None = None
    city: str | None = None
    status: str | None = None


class ClinicResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    address: str | None
    city: str | None
    country: str | None
    phone: str | None
    email: str | None
    logo_url: str | None
    opening_hours: dict | None
    timezone: str
    notes: str | None
    status: str
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class ClinicRoomCreate(BaseModel):
    name: str = Field(..., max_length=100)
    chair_number: int | None = None
    status: str = Field(default="available", max_length=20)
    notes: str | None = None


class ClinicRoomUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    chair_number: int | None = None
    status: str | None = Field(None, max_length=20)
    notes: str | None = None


class ClinicRoomFilter(BaseModel):
    search: str | None = None
    name: str | None = None
    status: str | None = None
    clinic_id: UUID | None = None


class ClinicRoomResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    name: str
    chair_number: int | None
    status: str
    notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
