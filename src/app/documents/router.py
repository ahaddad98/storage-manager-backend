from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.documents.repository import ActivityLogRepository, DocumentRepository
from app.documents.schema import (
    ActivityLogFilter,
    ActivityLogResponse,
    DocumentCreate,
    DocumentFilter,
    DocumentResponse,
    DocumentUpdate,
)
from app.documents.service import DocumentService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_document_service(
    repository: Annotated[DocumentRepository, Depends()],
    activity_log_repository: Annotated[ActivityLogRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> DocumentService:
    return DocumentService(repository, activity_log_repository, tenant)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_MANAGE))],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    return await service.create(data)


@router.get("", response_model=Page[DocumentResponse])
async def list_documents(
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_READ))],
    service: Annotated[DocumentService, Depends(get_document_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    treatment_id: UUID | None = Query(default=None),
    invoice_id: UUID | None = Query(default=None),
    document_type: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[DocumentResponse]:
    filters = DocumentFilter(
        search=search,
        patient_id=patient_id,
        treatment_id=treatment_id,
        invoice_id=invoice_id,
        document_type=document_type,
        clinic_id=clinic_id,
    )
    if not any([search, patient_id, treatment_id, invoice_id, document_type, clinic_id]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/activity-logs", response_model=Page[ActivityLogResponse])
async def list_activity_logs(
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_READ))],
    service: Annotated[DocumentService, Depends(get_document_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    event_type: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[ActivityLogResponse]:
    filters = ActivityLogFilter(
        search=search,
        patient_id=patient_id,
        clinic_id=clinic_id,
        user_id=user_id,
        event_type=event_type,
    )
    if not any([search, patient_id, clinic_id, user_id, event_type]):
        filters = None
    return await service.list_activity_logs(params=params, filters=filters, order_by=order_by)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_READ))],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    return await service.get_by_id(document_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_MANAGE))],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    return await service.update(document_id, data)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_MANAGE))],
    service: Annotated[DocumentService, Depends(get_document_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(document_id, hard=hard)


@router.post("/{document_id}/restore", response_model=DocumentResponse)
async def restore_document(
    document_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DOCUMENTS_MANAGE))],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    return await service.restore(document_id)
