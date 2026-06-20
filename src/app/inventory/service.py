from uuid import UUID

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
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class InventoryService:
    def __init__(
        self,
        supplier_repository: SupplierRepository,
        item_repository: InventoryItemRepository,
        movement_repository: StockMovementRepository,
        tenant: TenantContext,
    ):
        self.supplier_repository = supplier_repository
        self.item_repository = item_repository
        self.movement_repository = movement_repository
        self.tenant = tenant

    async def create_supplier(self, data: SupplierCreate) -> SupplierResponse:
        supplier = await self.supplier_repository.create(data)
        return SupplierResponse.model_validate(supplier)

    async def get_supplier(self, supplier_id: UUID) -> SupplierResponse:
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None:
            raise NotFoundException(f"Supplier {supplier_id} not found")
        return SupplierResponse.model_validate(supplier)

    async def list_suppliers(
        self,
        params: PaginationParams,
        filters: SupplierFilter | None = None,
        order_by: str | None = None,
    ) -> Page[SupplierResponse]:
        page = await self.supplier_repository.list(
            params=params, filters=filters, order_by=order_by
        )
        return Page.create(
            items=[SupplierResponse.model_validate(s) for s in page.items],
            total=page.total,
            params=params,
        )

    async def update_supplier(self, supplier_id: UUID, data: SupplierUpdate) -> SupplierResponse:
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None:
            raise NotFoundException(f"Supplier {supplier_id} not found")
        updated = await self.supplier_repository.update(supplier, data)
        return SupplierResponse.model_validate(updated)

    async def delete_supplier(self, supplier_id: UUID, hard: bool = False) -> None:
        deleted = await self.supplier_repository.delete(supplier_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Supplier {supplier_id} not found")

    async def create_item(self, data: InventoryItemCreate) -> InventoryItemResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        item = await self.item_repository.create(data)
        return InventoryItemResponse.model_validate(item)

    async def get_item(self, item_id: UUID) -> InventoryItemResponse:
        item = await self.item_repository.get_by_id(item_id)
        if item is None:
            raise NotFoundException(f"Inventory item {item_id} not found")
        return InventoryItemResponse.model_validate(item)

    async def list_items(
        self,
        params: PaginationParams,
        filters: InventoryItemFilter | None = None,
        order_by: str | None = None,
    ) -> Page[InventoryItemResponse]:
        page = await self.item_repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[InventoryItemResponse.model_validate(i) for i in page.items],
            total=page.total,
            params=params,
        )

    async def update_item(self, item_id: UUID, data: InventoryItemUpdate) -> InventoryItemResponse:
        item = await self.item_repository.get_by_id(item_id)
        if item is None:
            raise NotFoundException(f"Inventory item {item_id} not found")
        updated = await self.item_repository.update(item, data)
        return InventoryItemResponse.model_validate(updated)

    async def delete_item(self, item_id: UUID, hard: bool = False) -> None:
        deleted = await self.item_repository.delete(item_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Inventory item {item_id} not found")

    async def create_movement(self, data: StockMovementCreate) -> StockMovementResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        item = await self.item_repository.get_by_id(data.item_id)
        if item is None:
            raise NotFoundException(f"Inventory item {data.item_id} not found")
        self.tenant.require_clinic_access(item.clinic_id)
        if item.clinic_id != data.clinic_id:
            raise NotFoundException(f"Inventory item {data.item_id} not found")
        movement = await self.movement_repository.create(data, created_by=self.tenant.user_id)
        if data.movement_type == "in":
            new_qty = item.quantity + data.quantity
        elif data.movement_type == "out":
            new_qty = max(0, item.quantity - data.quantity)
        else:
            new_qty = data.quantity
        await self.item_repository.update_from_dict(item, {"quantity": new_qty})
        return StockMovementResponse.model_validate(movement)

    async def list_movements(
        self,
        params: PaginationParams,
        filters: StockMovementFilter | None = None,
        order_by: str | None = None,
    ) -> Page[StockMovementResponse]:
        page = await self.movement_repository.list(
            params=params, filters=filters, order_by=order_by
        )
        return Page.create(
            items=[StockMovementResponse.model_validate(m) for m in page.items],
            total=page.total,
            params=params,
        )

    async def get_movement(self, movement_id: UUID) -> StockMovementResponse:
        movement = await self.movement_repository.get_by_id(movement_id)
        if movement is None:
            raise NotFoundException(f"Stock movement {movement_id} not found")
        return StockMovementResponse.model_validate(movement)
