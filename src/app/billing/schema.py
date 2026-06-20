from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    clinic_id: UUID
    patient_id: UUID
    invoice_number: str = Field(..., max_length=50)
    invoice_date: date
    due_date: date | None = None
    subtotal: Decimal = Field(default=Decimal("0"))
    discount: Decimal = Field(default=Decimal("0"))
    total_amount: Decimal = Field(default=Decimal("0"))
    amount_paid: Decimal = Field(default=Decimal("0"))
    status: str = Field(default="unpaid", max_length=20)
    notes: str | None = None


class InvoiceUpdate(BaseModel):
    invoice_number: str | None = Field(None, max_length=50)
    invoice_date: date | None = None
    due_date: date | None = None
    subtotal: Decimal | None = None
    discount: Decimal | None = None
    total_amount: Decimal | None = None
    amount_paid: Decimal | None = None
    status: str | None = Field(None, max_length=20)
    notes: str | None = None


class InvoiceFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    status: str | None = None
    clinic_id: UUID | None = None
    invoice_date_from: date | None = None
    invoice_date_to: date | None = None


class InvoiceItemCreate(BaseModel):
    description: str = Field(..., max_length=500)
    treatment_ref: str | None = Field(None, max_length=255)
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(default=Decimal("0"))
    total: Decimal = Field(default=Decimal("0"))


class InvoiceItemUpdate(BaseModel):
    description: str | None = Field(None, max_length=500)
    treatment_ref: str | None = Field(None, max_length=255)
    quantity: int | None = Field(None, ge=1)
    unit_price: Decimal | None = None
    total: Decimal | None = None


class InvoiceItemFilter(BaseModel):
    search: str | None = None
    invoice_id: UUID | None = None


class PaymentCreate(BaseModel):
    clinic_id: UUID
    patient_id: UUID
    invoice_id: UUID | None = None
    amount: Decimal
    payment_date: date
    method: str = Field(..., max_length=30)
    reference: str | None = Field(None, max_length=100)
    notes: str | None = None
    received_by: UUID | None = None


class PaymentUpdate(BaseModel):
    amount: Decimal | None = None
    payment_date: date | None = None
    method: str | None = Field(None, max_length=30)
    reference: str | None = Field(None, max_length=100)
    notes: str | None = None
    received_by: UUID | None = None
    invoice_id: UUID | None = None


class PaymentFilter(BaseModel):
    search: str | None = None
    patient_id: UUID | None = None
    invoice_id: UUID | None = None
    method: str | None = None
    clinic_id: UUID | None = None
    payment_date_from: date | None = None
    payment_date_to: date | None = None


class InvoiceItemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    invoice_id: UUID
    description: str
    treatment_ref: str | None
    quantity: int
    unit_price: Decimal
    total: Decimal
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class InvoiceResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    created_by: UUID | None
    patient_id: UUID
    invoice_number: str
    invoice_date: date
    due_date: date | None
    subtotal: Decimal
    discount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    status: str
    notes: str | None
    items: list[InvoiceItemResponse] = []
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    clinic_id: UUID
    patient_id: UUID
    invoice_id: UUID | None
    amount: Decimal
    payment_date: date
    method: str
    reference: str | None
    notes: str | None
    received_by: UUID | None
    created_on: datetime
    updated_on: datetime

    model_config = {"from_attributes": True}
