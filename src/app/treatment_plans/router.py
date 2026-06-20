from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.treatment_plans.repository import TreatmentItemRepository, TreatmentPlanRepository
from app.treatment_plans.schema import (
    TreatmentItemCreate,
    TreatmentItemFilter,
    TreatmentItemResponse,
    TreatmentItemUpdate,
    TreatmentPlanCreate,
    TreatmentPlanFilter,
    TreatmentPlanResponse,
    TreatmentPlanUpdate,
)
from app.treatment_plans.service import TreatmentPlanService
from core.business_modules import ModuleKey
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.modules import require_enabled_module
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter(dependencies=[Depends(require_enabled_module(ModuleKey.TREATMENTS))])


def get_treatment_plan_service(
    repository: Annotated[TreatmentPlanRepository, Depends()],
    item_repository: Annotated[TreatmentItemRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> TreatmentPlanService:
    return TreatmentPlanService(repository, item_repository, tenant)


@router.post("", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment_plan(
    data: TreatmentPlanCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentPlanResponse:
    return await service.create(data)


@router.get("", response_model=Page[TreatmentPlanResponse])
async def list_treatment_plans(
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_READ))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    dentist_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[TreatmentPlanResponse]:
    filters = TreatmentPlanFilter(
        search=search,
        patient_id=patient_id,
        dentist_id=dentist_id,
        status=status,
        clinic_id=clinic_id,
    )
    if not any([search, patient_id, dentist_id, status, clinic_id]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/{plan_id}", response_model=TreatmentPlanResponse)
async def get_treatment_plan(
    plan_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_READ))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentPlanResponse:
    return await service.get_by_id(plan_id)


@router.patch("/{plan_id}", response_model=TreatmentPlanResponse)
async def update_treatment_plan(
    plan_id: UUID,
    data: TreatmentPlanUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentPlanResponse:
    return await service.update(plan_id, data)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment_plan(
    plan_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(plan_id, hard=hard)


@router.post("/{plan_id}/restore", response_model=TreatmentPlanResponse)
async def restore_treatment_plan(
    plan_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentPlanResponse:
    return await service.restore(plan_id)


@router.post(
    "/{plan_id}/items",
    response_model=TreatmentItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_treatment_item(
    plan_id: UUID,
    data: TreatmentItemCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentItemResponse:
    return await service.create_item(plan_id, data)


@router.get("/{plan_id}/items", response_model=Page[TreatmentItemResponse])
async def list_treatment_items(
    plan_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_READ))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[TreatmentItemResponse]:
    filters = TreatmentItemFilter(search=search, status=status, priority=priority)
    if not any([search, status, priority]):
        filters = None
    return await service.list_items(plan_id, params=params, filters=filters, order_by=order_by)


@router.get("/{plan_id}/items/{item_id}", response_model=TreatmentItemResponse)
async def get_treatment_item(
    plan_id: UUID,
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_READ))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentItemResponse:
    return await service.get_item(plan_id, item_id)


@router.patch("/{plan_id}/items/{item_id}", response_model=TreatmentItemResponse)
async def update_treatment_item(
    plan_id: UUID,
    item_id: UUID,
    data: TreatmentItemUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
) -> TreatmentItemResponse:
    return await service.update_item(plan_id, item_id, data)


@router.delete("/{plan_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment_item(
    plan_id: UUID,
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.TREATMENTS_MANAGE))],
    service: Annotated[TreatmentPlanService, Depends(get_treatment_plan_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_item(plan_id, item_id, hard=hard)
