from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.patients.repository import MedicalHistoryRepository, PatientRepository
from app.patients.schema import (
    MedicalHistoryResponse,
    MedicalHistoryUpdate,
    PatientCreate,
    PatientFilter,
    PatientResponse,
    PatientUpdate,
)
from app.patients.service import PatientService
from core.business_modules import ModuleKey
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.modules import require_enabled_module
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter(dependencies=[Depends(require_enabled_module(ModuleKey.PATIENTS))])


def get_patient_service(
    repository: Annotated[PatientRepository, Depends()],
    medical_history_repository: Annotated[MedicalHistoryRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> PatientService:
    return PatientService(repository, medical_history_repository, tenant)


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_CREATE))],
    service: Annotated[PatientService, Depends(get_patient_service)],
) -> PatientResponse:
    return await service.create(data)


@router.get("", response_model=Page[PatientResponse])
async def list_patients(
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_READ))],
    service: Annotated[PatientService, Depends(get_patient_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    full_name: str | None = Query(default=None),
    phone: str | None = Query(default=None),
    email: str | None = Query(default=None),
    status: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[PatientResponse]:
    filters = PatientFilter(
        search=search,
        full_name=full_name,
        phone=phone,
        email=email,
        status=status,
        clinic_id=clinic_id,
    )
    if not any([search, full_name, phone, email, status, clinic_id]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_READ))],
    service: Annotated[PatientService, Depends(get_patient_service)],
) -> PatientResponse:
    return await service.get_by_id(patient_id)


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    data: PatientUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_UPDATE))],
    service: Annotated[PatientService, Depends(get_patient_service)],
) -> PatientResponse:
    return await service.update(patient_id, data)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_DELETE))],
    service: Annotated[PatientService, Depends(get_patient_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(patient_id, hard=hard)


@router.post("/{patient_id}/restore", response_model=PatientResponse)
async def restore_patient(
    patient_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_UPDATE))],
    service: Annotated[PatientService, Depends(get_patient_service)],
) -> PatientResponse:
    return await service.restore(patient_id)


@router.get("/{patient_id}/medical-history", response_model=MedicalHistoryResponse)
async def get_medical_history(
    patient_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_READ))],
    service: Annotated[PatientService, Depends(get_patient_service)],
) -> MedicalHistoryResponse:
    return await service.get_medical_history(patient_id)


@router.put("/{patient_id}/medical-history", response_model=MedicalHistoryResponse)
async def upsert_medical_history(
    patient_id: UUID,
    data: MedicalHistoryUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.PATIENTS_UPDATE))],
    service: Annotated[PatientService, Depends(get_patient_service)],
) -> MedicalHistoryResponse:
    return await service.upsert_medical_history(patient_id, data)
