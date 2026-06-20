from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CatalogInventoryItem(BaseModel):
    sku: str
    name: str
    category: str
    unit: str
    min_stock_level: int
    quantity: int = 0
    cost_per_unit: Decimal = Decimal("0")
    notes: str | None = None


class CatalogTreatmentTemplate(BaseModel):
    code: str
    category: str
    name: str
    description: str | None = None
    estimated_cost: Decimal = Decimal("0")
    priority: str = "normal"


class PresetCatalogResponse(BaseModel):
    business_type: str
    title: str
    description: str
    inventory_items: list[CatalogInventoryItem]
    treatment_templates: list[CatalogTreatmentTemplate]


class ApplyInventoryStarterKitRequest(BaseModel):
    clinic_id: UUID


class AppliedInventoryItem(BaseModel):
    sku: str
    name: str
    status: str
    item_id: UUID | None = None


class ApplyInventoryStarterKitResponse(BaseModel):
    clinic_id: UUID
    created_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    items: list[AppliedInventoryItem]
    applied_on: datetime
