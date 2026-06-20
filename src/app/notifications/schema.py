from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationFilter(BaseModel):
    search: str | None = None
    notification_type: str | None = None
    is_read: bool | None = None
    user_id: UUID | None = None


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    notification_type: str
    title: str
    message: str
    is_read: bool
    related_entity_type: str | None
    related_entity_id: UUID | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class NotificationCreate(BaseModel):
    user_id: UUID
    notification_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=255)
    message: str
    related_entity_type: str | None = Field(None, max_length=50)
    related_entity_id: UUID | None = None
