from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.dental_chart.model import DentalChart, ToothRecord
from app.dental_chart.schema import (
    DentalChartCreate,
    DentalChartFilter,
    DentalChartUpdate,
    ToothRecordCreate,
    ToothRecordFilter,
    ToothRecordUpdate,
)
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class DentalChartRepository(
    TenantRepository[DentalChart, DentalChartCreate, DentalChartUpdate, DentalChartFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            DentalChart,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "created_on": DentalChart.created_on.asc(),
        "-created_on": DentalChart.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return [selectinload(DentalChart.teeth)]

    def build_filter_conditions(
        self, filters: DentalChartFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.patient_id:
            conditions.append(self.model.patient_id == filters.patient_id)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.search:
            conditions.append(self.model.notes.ilike(f"%{filters.search}%"))
        return conditions

    async def get_by_patient_id(self, patient_id: UUID) -> DentalChart | None:
        query = self._base_query().where(
            self.model.patient_id == patient_id,
            self.model.organization_id == self.organization_id,
        )
        if self.clinic_id:
            query = query.where(self.model.clinic_id == self.clinic_id)
        elif self.clinic_ids is not None:
            if self.clinic_ids:
                query = query.where(self.model.clinic_id.in_(self.clinic_ids))
            else:
                query = query.where(false())
        for rel in self.default_relationships():
            query = query.options(rel)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class ToothRecordRepository(
    TenantRepository[ToothRecord, ToothRecordCreate, ToothRecordUpdate, ToothRecordFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(ToothRecord, session=session, organization_id=tenant.organization_id)

    ORDER_BY_MAP = {
        "tooth_number": ToothRecord.tooth_number.asc(),
        "-tooth_number": ToothRecord.tooth_number.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: ToothRecordFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.chart_id:
            conditions.append(self.model.chart_id == filters.chart_id)
        if filters.tooth_number is not None:
            conditions.append(self.model.tooth_number == filters.tooth_number)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.diagnosis.ilike(pattern),
                    self.model.notes.ilike(pattern),
                )
            )
        return conditions

    async def get_by_id_for_chart(self, tooth_id: UUID, chart_id: UUID) -> ToothRecord | None:
        query = self._base_query().where(
            self.model.id == tooth_id,
            self.model.chart_id == chart_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
