from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.clinics.repository import ClinicRepository, ClinicRoomRepository
from app.clinics.schema import (
    ClinicCreate,
    ClinicFilter,
    ClinicResponse,
    ClinicRoomCreate,
    ClinicRoomFilter,
    ClinicRoomResponse,
    ClinicRoomUpdate,
    ClinicUpdate,
)
from app.clinics.service import ClinicService
from app.staff.repository import ClinicAssignmentRepository, MembershipRepository
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_clinic_service(
    repository: Annotated[ClinicRepository, Depends()],
    room_repository: Annotated[ClinicRoomRepository, Depends()],
    membership_repository: Annotated[MembershipRepository, Depends()],
    assignment_repository: Annotated[ClinicAssignmentRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> ClinicService:
    return ClinicService(
        repository,
        room_repository,
        membership_repository,
        assignment_repository,
        tenant,
    )


@router.post("", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic(
    data: ClinicCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicResponse:
    return await service.create(data)


@router.get("", response_model=Page[ClinicResponse])
async def list_clinics(
    service: Annotated[ClinicService, Depends(get_clinic_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    name: str | None = Query(default=None),
    city: str | None = Query(default=None),
    status: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[ClinicResponse]:
    filters = ClinicFilter(search=search, name=name, city=city, status=status)
    if not any([search, name, city, status]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/{clinic_id}", response_model=ClinicResponse)
async def get_clinic(
    clinic_id: UUID,
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicResponse:
    return await service.get_by_id(clinic_id)


@router.patch("/{clinic_id}", response_model=ClinicResponse)
async def update_clinic(
    clinic_id: UUID,
    data: ClinicUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicResponse:
    return await service.update(clinic_id, data)


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinic(
    clinic_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(clinic_id, hard=hard)


@router.post("/{clinic_id}/restore", response_model=ClinicResponse)
async def restore_clinic(
    clinic_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicResponse:
    return await service.restore(clinic_id)


@router.post(
    "/{clinic_id}/rooms",
    response_model=ClinicRoomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_clinic_room(
    clinic_id: UUID,
    data: ClinicRoomCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicRoomResponse:
    return await service.create_room(clinic_id, data)


@router.get("/{clinic_id}/rooms", response_model=Page[ClinicRoomResponse])
async def list_clinic_rooms(
    clinic_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[ClinicRoomResponse]:
    filters = ClinicRoomFilter(search=search, name=name, status=status)
    if not any([search, name, status]):
        filters = None
    return await service.list_rooms(clinic_id, params=params, filters=filters, order_by=order_by)


@router.get("/{clinic_id}/rooms/{room_id}", response_model=ClinicRoomResponse)
async def get_clinic_room(
    clinic_id: UUID,
    room_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicRoomResponse:
    return await service.get_room(clinic_id, room_id)


@router.patch("/{clinic_id}/rooms/{room_id}", response_model=ClinicRoomResponse)
async def update_clinic_room(
    clinic_id: UUID,
    room_id: UUID,
    data: ClinicRoomUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicRoomResponse:
    return await service.update_room(clinic_id, room_id, data)


@router.delete("/{clinic_id}/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinic_room(
    clinic_id: UUID,
    room_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_room(clinic_id, room_id, hard=hard)


@router.post("/{clinic_id}/rooms/{room_id}/restore", response_model=ClinicRoomResponse)
async def restore_clinic_room(
    clinic_id: UUID,
    room_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.CLINICS_MANAGE))],
    service: Annotated[ClinicService, Depends(get_clinic_service)],
) -> ClinicRoomResponse:
    return await service.restore_room(clinic_id, room_id)
