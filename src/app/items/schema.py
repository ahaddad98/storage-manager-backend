from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None


class ItemFilter(BaseModel):
    name: str | None = None


class ItemResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
