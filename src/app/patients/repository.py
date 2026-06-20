from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.patients.model import MedicalHistory, Patient
from app.patients.schema import MedicalHistoryUpdate, PatientCreate, PatientFilter, PatientUpdate
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class PatientRepository(TenantRepository[Patient, PatientCreate, PatientUpdate, PatientFilter]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            Patient,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "full_name": Patient.full_name.asc(),
        "-full_name": Patient.full_name.desc(),
        "created_on": Patient.created_on.asc(),
        "-created_on": Patient.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return [selectinload(Patient.medical_history)]

    def build_filter_conditions(self, filters: PatientFilter | None) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.full_name.ilike(pattern),
                    self.model.phone.ilike(pattern),
                    self.model.email.ilike(pattern),
                )
            )
        if filters.full_name:
            conditions.append(self.model.full_name.ilike(f"%{filters.full_name}%"))
        if filters.phone:
            conditions.append(self.model.phone.ilike(f"%{filters.phone}%"))
        if filters.email:
            conditions.append(self.model.email.ilike(f"%{filters.email}%"))
        if filters.status:
            conditions.append(self.model.status == filters.status)
        return conditions


class MedicalHistoryRepository(TenantRepository):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(MedicalHistory, session=session, organization_id=tenant.organization_id)

    async def get_by_patient_id(self, patient_id: UUID) -> MedicalHistory | None:
        query = self._base_query().where(
            self.model.patient_id == patient_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def upsert_for_patient(
        self, patient_id: UUID, data: MedicalHistoryUpdate
    ) -> MedicalHistory:
        existing = await self.get_by_patient_id(patient_id)
        if existing:
            return await self.update(existing, data)
        return await self.create(data, patient_id=patient_id)
