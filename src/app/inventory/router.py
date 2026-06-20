from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.inventory.repository import (
    InventoryItemRepository,
    StockMovementRepository,
    SupplierRepository,
)
from app.inventory.schema import (
    InventoryItemCreate,
    InventoryItemFilter,
    InventoryItemResponse,
    InventoryItemUpdate,
    StockMovementCreate,
    StockMovementFilter,
    StockMovementResponse,
    SupplierCreate,
    SupplierFilter,
    SupplierResponse,
    SupplierUpdate,
)
from app.inventory.service import InventoryService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_inventory_service(
    supplier_repository: Annotated[SupplierRepository, Depends()],
    item_repository: Annotated[InventoryItemRepository, Depends()],
    movement_repository: Annotated[StockMovementRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> InventoryService:
    return InventoryService(supplier_repository, item_repository, movement_repository, tenant)


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SupplierResponse:
    return await service.create_supplier(data)


@router.get("/suppliers", response_model=Page[SupplierResponse])
async def list_suppliers(
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_READ))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    name: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[SupplierResponse]:
    filters = SupplierFilter(search=search, name=name)
    if not any([search, name]):
        filters = None
    return await service.list_suppliers(params=params, filters=filters, order_by=order_by)


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_READ))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SupplierResponse:
    return await service.get_supplier(supplier_id)


@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    data: SupplierUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SupplierResponse:
    return await service.update_supplier(supplier_id, data)


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_supplier(supplier_id, hard=hard)


@router.post("/items", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    data: InventoryItemCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryItemResponse:
    return await service.create_item(data)


@router.get("/items", response_model=Page[InventoryItemResponse])
async def list_inventory_items(
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_READ))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    name: str | None = Query(default=None),
    sku: str | None = Query(default=None),
    category: str | None = Query(default=None),
    item_status: str | None = Query(default=None, alias="status"),
    supplier_id: UUID | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    low_stock: bool | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[InventoryItemResponse]:
    filters = InventoryItemFilter(
        search=search,
        name=name,
        sku=sku,
        category=category,
        status=item_status,
        supplier_id=supplier_id,
        clinic_id=clinic_id,
        low_stock=low_stock,
    )
    if not any(
        [search, name, sku, category, item_status, supplier_id, clinic_id, low_stock is not None]
    ):
        filters = None
    return await service.list_items(params=params, filters=filters, order_by=order_by)


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_READ))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryItemResponse:
    return await service.get_item(item_id)


@router.patch("/items/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: UUID,
    data: InventoryItemUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryItemResponse:
    return await service.update_item(item_id, data)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete_item(item_id, hard=hard)


@router.post(
    "/movements", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED
)
async def create_stock_movement(
    data: StockMovementCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_MANAGE))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> StockMovementResponse:
    return await service.create_movement(data)


@router.get("/movements", response_model=Page[StockMovementResponse])
async def list_stock_movements(
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_READ))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    item_id: UUID | None = Query(default=None),
    movement_type: str | None = Query(default=None),
    clinic_id: UUID | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[StockMovementResponse]:
    filters = StockMovementFilter(
        search=search,
        item_id=item_id,
        movement_type=movement_type,
        clinic_id=clinic_id,
    )
    if not any([search, item_id, movement_type, clinic_id]):
        filters = None
    return await service.list_movements(params=params, filters=filters, order_by=order_by)


@router.get("/movements/{movement_id}", response_model=StockMovementResponse)
async def get_stock_movement(
    movement_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.INVENTORY_READ))],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> StockMovementResponse:
    return await service.get_movement(movement_id)
