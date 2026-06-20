from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dental_chart.repository import DentalChartRepository, ToothRecordRepository
from app.dental_chart.schema import (
    DentalChartCreate,
    DentalChartFilter,
    DentalChartResponse,
    DentalChartUpdate,
    ToothRecordCreate,
    ToothRecordFilter,
    ToothRecordResponse,
    ToothRecordUpdate,
)
from app.dental_chart.service import DentalChartService
from core.business_modules import ModuleKey
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.modules import require_enabled_module
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter(dependencies=[Depends(require_enabled_module(ModuleKey.DENTAL_CHART))])


def get_dental_chart_service(
    repository: Annotated[DentalChartRepository, Depends()],
    tooth_repository: Annotated[ToothRecordRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> DentalChartService:
    return DentalChartService(repository, tooth_repository, tenant)


@router.post("", response_model=DentalChartResponse, status_code=status.HTTP_201_CREATED)
async def create_dental_chart(
    data: DentalChartCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_MANAGE))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> DentalChartResponse:
    return await service.create(data)


@router.get("", response_model=Page[DentalChartResponse])
async def list_dental_charts(
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_READ))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[DentalChartResponse]:
    filters = DentalChartFilter(
        search=search, patient_id=patient_id, status=status, clinic_id=clinic_id
    )
    if not any([search, patient_id, status, clinic_id]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/patient/{patient_id}", response_model=DentalChartResponse)
async def get_dental_chart_by_patient(
    patient_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_READ))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> DentalChartResponse:
    return await service.get_by_patient_id(patient_id)


@router.get("/{chart_id}", response_model=DentalChartResponse)
async def get_dental_chart(
    chart_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_READ))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> DentalChartResponse:
    return await service.get_by_id(chart_id)


@router.patch("/{chart_id}", response_model=DentalChartResponse)
async def update_dental_chart(
    chart_id: UUID,
    data: DentalChartUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_MANAGE))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> DentalChartResponse:
    return await service.update(chart_id, data)


@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dental_chart(
    chart_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_MANAGE))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(chart_id, hard=hard)


@router.post(
    "/{chart_id}/teeth",
    response_model=ToothRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tooth_record(
    chart_id: UUID,
    data: ToothRecordCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_MANAGE))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> ToothRecordResponse:
    return await service.create_tooth(chart_id, data)


@router.get("/{chart_id}/teeth", response_model=Page[ToothRecordResponse])
async def list_tooth_records(
    chart_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_READ))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    tooth_number: int | None = Query(default=None),
    status: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[ToothRecordResponse]:
    filters = ToothRecordFilter(search=search, tooth_number=tooth_number, status=status)
    if not any([search, tooth_number, status]):
        filters = None
    return await service.list_teeth(chart_id, params=params, filters=filters, order_by=order_by)


@router.get("/{chart_id}/teeth/{tooth_id}", response_model=ToothRecordResponse)
async def get_tooth_record(
    chart_id: UUID,
    tooth_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_READ))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> ToothRecordResponse:
    return await service.get_tooth(chart_id, tooth_id)


@router.patch("/{chart_id}/teeth/{tooth_id}", response_model=ToothRecordResponse)
async def update_tooth_record(
    chart_id: UUID,
    tooth_id: UUID,
    data: ToothRecordUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_MANAGE))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
) -> ToothRecordResponse:
    return await service.update_tooth(chart_id, tooth_id, data)


@router.delete("/{chart_id}/teeth/{tooth_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tooth_record(
    chart_id: UUID,
    tooth_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.DENTAL_CHART_MANAGE))],
    service: Annotated[DentalChartService, Depends(get_dental_chart_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_tooth(chart_id, tooth_id, hard=hard)
