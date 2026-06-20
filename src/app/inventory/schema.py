from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., max_length=255)
    contact_person: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    address: str | None = None
    notes: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    contact_person: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    address: str | None = None
    notes: str | None = None


class SupplierFilter(BaseModel):
    search: str | None = None
    name: str | None = None


class InventoryItemCreate(BaseModel):
    clinic_id: UUID
    name: str = Field(..., max_length=255)
    sku: str | None = Field(None, max_length=50)
    category: str | None = Field(None, max_length=100)
    status: str = Field(default="ok", max_length=20)
    quantity: int = Field(default=0, ge=0)
    unit: str = Field(default="unit", max_length=30)
    min_stock_level: int = Field(default=10, ge=0)
    cost_per_unit: Decimal = Field(default=Decimal("0"))
    supplier_id: UUID | None = None
    expiry_date: date | None = None
    notes: str | None = None


class InventoryItemUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    sku: str | None = Field(None, max_length=50)
    category: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=20)
    quantity: int | None = Field(None, ge=0)
    unit: str | None = Field(None, max_length=30)
    min_stock_level: int | None = Field(None, ge=0)
    cost_per_unit: Decimal | None = None
    supplier_id: UUID | None = None
    expiry_date: date | None = None
    notes: str | None = None


class InventoryItemFilter(BaseModel):
    search: str | None = None
    name: str | None = None
    sku: str | None = None
    category: str | None = None
    status: str | None = None
    supplier_id: UUID | None = None
    clinic_id: UUID | None = None
    low_stock: bool | None = None


class StockMovementCreate(BaseModel):
    clinic_id: UUID
    item_id: UUID
    movement_type: str = Field(..., max_length=20)
    quantity: int = Field(..., ge=1)
    reason: str | None = Field(None, max_length=255)


class StockMovementUpdate(BaseModel):
    reason: str | None = Field(None, max_length=255)


class StockMovementFilter(BaseModel):
    search: str | None = None
    item_id: UUID | None = None
    movement_type: str | None = None
    clinic_id: UUID | None = None


class SupplierResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class InventoryItemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    name: str
    sku: str | None
    category: str | None
    status: str
    quantity: int
    unit: str
    min_stock_level: int
    cost_per_unit: Decimal
    supplier_id: UUID | None
    expiry_date: date | None
    notes: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class StockMovementResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    created_by: UUID | None
    item_id: UUID
    movement_type: str
    quantity: int
    reason: str | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
