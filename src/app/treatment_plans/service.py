from decimal import Decimal
from uuid import UUID

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
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class TreatmentPlanService:
    def __init__(
        self,
        repository: TreatmentPlanRepository,
        item_repository: TreatmentItemRepository,
        tenant: TenantContext,
    ):
        self.repository = repository
        self.item_repository = item_repository
        self.tenant = tenant

    async def create(self, data: TreatmentPlanCreate) -> TreatmentPlanResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        plan = await self.repository.create(data, created_by=self.tenant.user_id)
        return TreatmentPlanResponse.model_validate(plan)

    async def get_by_id(self, plan_id: UUID) -> TreatmentPlanResponse:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        return TreatmentPlanResponse.model_validate(plan)

    async def list(
        self,
        params: PaginationParams,
        filters: TreatmentPlanFilter | None = None,
        order_by: str | None = None,
    ) -> Page[TreatmentPlanResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[TreatmentPlanResponse.model_validate(p) for p in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, plan_id: UUID, data: TreatmentPlanUpdate) -> TreatmentPlanResponse:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        updated = await self.repository.update(plan, data)
        return TreatmentPlanResponse.model_validate(updated)

    async def delete(self, plan_id: UUID, hard: bool = False) -> None:
        deleted = await self.repository.delete(plan_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Treatment plan {plan_id} not found")

    async def restore(self, plan_id: UUID) -> TreatmentPlanResponse:
        plan = await self.repository.restore(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found or not deleted")
        return TreatmentPlanResponse.model_validate(plan)

    async def _recalculate_total(self, plan_id: UUID) -> None:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            return
        items = await self.item_repository.list_raw(
            filters=TreatmentItemFilter(plan_id=plan_id),
            limit=1000,
        )
        total = sum((item.estimated_cost for item in items), Decimal("0"))
        await self.repository.update_from_dict(plan, {"estimated_total": total})

    async def create_item(self, plan_id: UUID, data: TreatmentItemCreate) -> TreatmentItemResponse:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        item = await self.item_repository.create(data, plan_id=plan_id)
        await self._recalculate_total(plan_id)
        return TreatmentItemResponse.model_validate(item)

    async def list_items(
        self,
        plan_id: UUID,
        params: PaginationParams,
        filters: TreatmentItemFilter | None = None,
        order_by: str | None = None,
    ) -> Page[TreatmentItemResponse]:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        item_filters = filters or TreatmentItemFilter()
        item_filters.plan_id = plan_id
        page = await self.item_repository.list(
            params=params, filters=item_filters, order_by=order_by
        )
        return Page.create(
            items=[TreatmentItemResponse.model_validate(i) for i in page.items],
            total=page.total,
            params=params,
        )

    async def get_item(self, plan_id: UUID, item_id: UUID) -> TreatmentItemResponse:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        item = await self.item_repository.get_by_id_for_plan(item_id, plan_id)
        if item is None:
            raise NotFoundException(f"Treatment item {item_id} not found in plan {plan_id}")
        return TreatmentItemResponse.model_validate(item)

    async def update_item(
        self, plan_id: UUID, item_id: UUID, data: TreatmentItemUpdate
    ) -> TreatmentItemResponse:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        item = await self.item_repository.get_by_id_for_plan(item_id, plan_id)
        if item is None:
            raise NotFoundException(f"Treatment item {item_id} not found in plan {plan_id}")
        updated = await self.item_repository.update(item, data)
        await self._recalculate_total(plan_id)
        return TreatmentItemResponse.model_validate(updated)

    async def delete_item(self, plan_id: UUID, item_id: UUID, hard: bool = False) -> None:
        plan = await self.repository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundException(f"Treatment plan {plan_id} not found")
        item = await self.item_repository.get_by_id_for_plan(item_id, plan_id)
        if item is None:
            raise NotFoundException(f"Treatment item {item_id} not found in plan {plan_id}")
        await self.item_repository.delete(item_id, hard=hard)
        await self._recalculate_total(plan_id)
