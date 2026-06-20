from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.appointments.model import Appointment
from app.appointments.schema import AppointmentCreate, AppointmentFilter, AppointmentUpdate
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class AppointmentRepository(
    TenantRepository[Appointment, AppointmentCreate, AppointmentUpdate, AppointmentFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            Appointment,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "start_time": Appointment.start_time.asc(),
        "-start_time": Appointment.start_time.desc(),
        "created_on": Appointment.created_on.asc(),
        "-created_on": Appointment.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: AppointmentFilter | None
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
        if filters.room_id:
            conditions.append(self.model.room_id == filters.room_id)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.start_from:
            conditions.append(self.model.start_time >= filters.start_from)
        if filters.start_to:
            conditions.append(self.model.start_time <= filters.start_to)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.treatment_type.ilike(pattern),
                    self.model.notes.ilike(pattern),
                )
            )
        return conditions
