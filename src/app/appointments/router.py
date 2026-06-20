from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.appointments.repository import AppointmentRepository
from app.appointments.schema import (
    AppointmentCreate,
    AppointmentFilter,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.appointments.service import AppointmentService
from core.business_modules import ModuleKey
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.modules import require_enabled_module
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter(dependencies=[Depends(require_enabled_module(ModuleKey.APPOINTMENTS))])


def get_appointment_service(
    repository: Annotated[AppointmentRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> AppointmentService:
    return AppointmentService(repository, tenant)


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.APPOINTMENTS_MANAGE))],
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
) -> AppointmentResponse:
    return await service.create(data)


@router.get("", response_model=Page[AppointmentResponse])
async def list_appointments(
    _user: Annotated[dict, Depends(require_permission(Permission.APPOINTMENTS_READ))],
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    dentist_id: UUID | None = Query(default=None),
    room_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    start_from: datetime | None = Query(default=None),
    start_to: datetime | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[AppointmentResponse]:
    filters = AppointmentFilter(
        search=search,
        patient_id=patient_id,
        dentist_id=dentist_id,
        room_id=room_id,
        status=status,
        clinic_id=clinic_id,
        start_from=start_from,
        start_to=start_to,
    )
    if not any([search, patient_id, dentist_id, room_id, status, clinic_id, start_from, start_to]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.APPOINTMENTS_READ))],
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
) -> AppointmentResponse:
    return await service.get_by_id(appointment_id)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    data: AppointmentUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.APPOINTMENTS_MANAGE))],
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
) -> AppointmentResponse:
    return await service.update(appointment_id, data)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.APPOINTMENTS_MANAGE))],
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(appointment_id, hard=hard)


@router.post("/{appointment_id}/restore", response_model=AppointmentResponse)
async def restore_appointment(
    appointment_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.APPOINTMENTS_MANAGE))],
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
) -> AppointmentResponse:
    return await service.restore(appointment_id)
