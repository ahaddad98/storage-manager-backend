from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.inventory.model import InventoryItem, StockMovement, Supplier
from app.inventory.schema import (
    InventoryItemCreate,
    InventoryItemFilter,
    InventoryItemUpdate,
    StockMovementCreate,
    StockMovementFilter,
    StockMovementUpdate,
    SupplierCreate,
    SupplierFilter,
    SupplierUpdate,
)
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class SupplierRepository(
    TenantRepository[Supplier, SupplierCreate, SupplierUpdate, SupplierFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(Supplier, session=session, organization_id=tenant.organization_id)

    ORDER_BY_MAP = {
        "name": Supplier.name.asc(),
        "-name": Supplier.name.desc(),
        "created_on": Supplier.created_on.asc(),
        "-created_on": Supplier.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(self, filters: SupplierFilter | None) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.name:
            conditions.append(self.model.name.ilike(f"%{filters.name}%"))
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.name.ilike(pattern),
                    self.model.contact_person.ilike(pattern),
                    self.model.email.ilike(pattern),
                )
            )
        return conditions


class InventoryItemRepository(
    TenantRepository[InventoryItem, InventoryItemCreate, InventoryItemUpdate, InventoryItemFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            InventoryItem,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "name": InventoryItem.name.asc(),
        "-name": InventoryItem.name.desc(),
        "quantity": InventoryItem.quantity.asc(),
        "-quantity": InventoryItem.quantity.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: InventoryItemFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.supplier_id:
            conditions.append(self.model.supplier_id == filters.supplier_id)
        if filters.category:
            conditions.append(self.model.category == filters.category)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.name:
            conditions.append(self.model.name.ilike(f"%{filters.name}%"))
        if filters.sku:
            conditions.append(self.model.sku.ilike(f"%{filters.sku}%"))
        if filters.low_stock:
            conditions.append(self.model.quantity <= self.model.min_stock_level)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.name.ilike(pattern),
                    self.model.sku.ilike(pattern),
                    self.model.category.ilike(pattern),
                )
            )
        return conditions


class StockMovementRepository(
    TenantRepository[StockMovement, StockMovementCreate, StockMovementUpdate, StockMovementFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            StockMovement,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "created_on": StockMovement.created_on.asc(),
        "-created_on": StockMovement.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: StockMovementFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.item_id:
            conditions.append(self.model.item_id == filters.item_id)
        if filters.movement_type:
            conditions.append(self.model.movement_type == filters.movement_type)
        if filters.search:
            conditions.append(self.model.reason.ilike(f"%{filters.search}%"))
        return conditions
