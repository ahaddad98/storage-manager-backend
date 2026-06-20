from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    business_type: str | None = Field(None, max_length=50)
    enabled_modules: list[str] | None = None
    logo_url: str | None = None
    billing_info: str | None = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    business_type: str
    enabled_modules: list[str] | None
    logo_url: str | None
    billing_info: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
