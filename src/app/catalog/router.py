from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.catalog.schema import (
    ApplyInventoryStarterKitRequest,
    ApplyInventoryStarterKitResponse,
    PresetCatalogResponse,
)
from app.catalog.service import PresetCatalogService
from app.clinics.repository import ClinicRepository
from app.inventory.repository import InventoryItemRepository
from core.business_modules import ModuleKey
from core.middleware.auth.exceptions import require_any_permission, require_permission
from core.middleware.auth.modules import require_enabled_module
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context

router = APIRouter(dependencies=[Depends(require_enabled_module(ModuleKey.CATALOG))])


def get_preset_catalog_service(
    clinic_repository: Annotated[ClinicRepository, Depends()],
    item_repository: Annotated[InventoryItemRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> PresetCatalogService:
    return PresetCatalogService(clinic_repository, item_repository, tenant)


@router.get("/presets", response_model=PresetCatalogResponse)
async def get_preset_catalog(
    _user: Annotated[
        dict,
        Depends(
            require_any_permission(
                [Permission.INVENTORY_READ, Permission.TREATMENTS_READ]
            )
        ),
    ],
    service: Annotated[PresetCatalogService, Depends(get_preset_catalog_service)],
) -> PresetCatalogResponse:
    return service.get_catalog()


@router.post(
    "/inventory-starter-kit/apply",
    response_model=ApplyInventoryStarterKitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_inventory_starter_kit(
    data: ApplyInventoryStarterKitRequest,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[PresetCatalogService, Depends(get_preset_catalog_service)],
) -> ApplyInventoryStarterKitResponse:
    return await service.apply_inventory_starter_kit(data.clinic_id)
