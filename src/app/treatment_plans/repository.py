from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.treatment_plans.model import TreatmentItem, TreatmentPlan
from app.treatment_plans.schema import (
    TreatmentItemCreate,
    TreatmentItemFilter,
    TreatmentItemUpdate,
    TreatmentPlanCreate,
    TreatmentPlanFilter,
    TreatmentPlanUpdate,
)
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class TreatmentPlanRepository(
    TenantRepository[TreatmentPlan, TreatmentPlanCreate, TreatmentPlanUpdate, TreatmentPlanFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            TreatmentPlan,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "title": TreatmentPlan.title.asc(),
        "-title": TreatmentPlan.title.desc(),
        "created_on": TreatmentPlan.created_on.asc(),
        "-created_on": TreatmentPlan.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return [selectinload(TreatmentPlan.items)]

    def build_filter_conditions(
        self, filters: TreatmentPlanFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.patient_id:
            conditions.append(self.model.patient_id == filters.patient_id)
        if filters.dentist_id:
            conditions.append(self.model.dentist_id == filters.dentist_id)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.title.ilike(pattern),
                    self.model.description.ilike(pattern),
                )
            )
        return conditions


class TreatmentItemRepository(
    TenantRepository[TreatmentItem, TreatmentItemCreate, TreatmentItemUpdate, TreatmentItemFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(TreatmentItem, session=session, organization_id=tenant.organization_id)

    ORDER_BY_MAP = {
        "name": TreatmentItem.name.asc(),
        "-name": TreatmentItem.name.desc(),
        "estimated_cost": TreatmentItem.estimated_cost.asc(),
        "-estimated_cost": TreatmentItem.estimated_cost.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: TreatmentItemFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.plan_id:
            conditions.append(self.model.plan_id == filters.plan_id)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.priority:
            conditions.append(self.model.priority == filters.priority)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.name.ilike(pattern),
                    self.model.description.ilike(pattern),
                )
            )
        return conditions

    async def get_by_id_for_plan(self, item_id: UUID, plan_id: UUID) -> TreatmentItem | None:
        query = self._base_query().where(
            self.model.id == item_id,
            self.model.plan_id == plan_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
