from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.billing.repository import InvoiceItemRepository, InvoiceRepository, PaymentRepository
from app.billing.schema import (
    InvoiceCreate,
    InvoiceFilter,
    InvoiceItemCreate,
    InvoiceItemFilter,
    InvoiceItemResponse,
    InvoiceItemUpdate,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentCreate,
    PaymentFilter,
    PaymentResponse,
    PaymentUpdate,
)
from app.billing.service import BillingService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_billing_service(
    invoice_repository: Annotated[InvoiceRepository, Depends()],
    invoice_item_repository: Annotated[InvoiceItemRepository, Depends()],
    payment_repository: Annotated[PaymentRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> BillingService:
    return BillingService(invoice_repository, invoice_item_repository, payment_repository, tenant)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceResponse:
    return await service.create_invoice(data)


@router.get("/invoices", response_model=Page[InvoiceResponse])
async def list_invoices(
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_READ))],
    service: Annotated[BillingService, Depends(get_billing_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    invoice_date_from: date | None = Query(default=None),
    invoice_date_to: date | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[InvoiceResponse]:
    filters = InvoiceFilter(
        search=search,
        patient_id=patient_id,
        status=status,
        clinic_id=clinic_id,
        invoice_date_from=invoice_date_from,
        invoice_date_to=invoice_date_to,
    )
    if not any([search, patient_id, status, clinic_id, invoice_date_from, invoice_date_to]):
        filters = None
    return await service.list_invoices(params=params, filters=filters, order_by=order_by)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_READ))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceResponse:
    return await service.get_invoice(invoice_id)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    data: InvoiceUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceResponse:
    return await service.update_invoice(invoice_id, data)


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_invoice(invoice_id, hard=hard)


@router.post("/invoices/{invoice_id}/restore", response_model=InvoiceResponse)
async def restore_invoice(
    invoice_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceResponse:
    return await service.restore_invoice(invoice_id)


@router.post(
    "/invoices/{invoice_id}/items",
    response_model=InvoiceItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invoice_item(
    invoice_id: UUID,
    data: InvoiceItemCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceItemResponse:
    return await service.create_invoice_item(invoice_id, data)


@router.get("/invoices/{invoice_id}/items", response_model=Page[InvoiceItemResponse])
async def list_invoice_items(
    invoice_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_READ))],
    service: Annotated[BillingService, Depends(get_billing_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[InvoiceItemResponse]:
    filters = InvoiceItemFilter(search=search) if search else None
    return await service.list_invoice_items(
        invoice_id, params=params, filters=filters, order_by=order_by
    )


@router.get("/invoices/{invoice_id}/items/{item_id}", response_model=InvoiceItemResponse)
async def get_invoice_item(
    invoice_id: UUID,
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_READ))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceItemResponse:
    return await service.get_invoice_item(invoice_id, item_id)


@router.patch("/invoices/{invoice_id}/items/{item_id}", response_model=InvoiceItemResponse)
async def update_invoice_item(
    invoice_id: UUID,
    item_id: UUID,
    data: InvoiceItemUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> InvoiceItemResponse:
    return await service.update_invoice_item(invoice_id, item_id, data)


@router.delete("/invoices/{invoice_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice_item(
    invoice_id: UUID,
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_invoice_item(invoice_id, item_id, hard=hard)


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> PaymentResponse:
    return await service.create_payment(data)


@router.get("/payments", response_model=Page[PaymentResponse])
async def list_payments(
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_READ))],
    service: Annotated[BillingService, Depends(get_billing_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    invoice_id: UUID | None = Query(default=None),
    method: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    payment_date_from: date | None = Query(default=None),
    payment_date_to: date | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[PaymentResponse]:
    filters = PaymentFilter(
        search=search,
        patient_id=patient_id,
        invoice_id=invoice_id,
        method=method,
        clinic_id=clinic_id,
        payment_date_from=payment_date_from,
        payment_date_to=payment_date_to,
    )
    if not any(
        [search, patient_id, invoice_id, method, clinic_id, payment_date_from, payment_date_to]
    ):
        filters = None
    return await service.list_payments(params=params, filters=filters, order_by=order_by)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_READ))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> PaymentResponse:
    return await service.get_payment(payment_id)


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    data: PaymentUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
) -> PaymentResponse:
    return await service.update_payment(payment_id, data)


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.BILLING_MANAGE))],
    service: Annotated[BillingService, Depends(get_billing_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_payment(payment_id, hard=hard)
