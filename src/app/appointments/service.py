from uuid import UUID

from app.appointments.repository import AppointmentRepository
from app.appointments.schema import (
    AppointmentCreate,
    AppointmentFilter,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.documents.activity import log_activity
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class AppointmentService:
    def __init__(self, repository: AppointmentRepository, tenant: TenantContext):
        self.repository = repository
        self.tenant = tenant

    async def create(self, data: AppointmentCreate) -> AppointmentResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        appointment = await self.repository.create(data, created_by=self.tenant.user_id)
        await log_activity(
            self.repository.session,
            organization_id=self.tenant.organization_id,
            clinic_id=appointment.clinic_id,
            patient_id=appointment.patient_id,
            user_id=self.tenant.user_id,
            event_type="appointment.created",
            description=f"Appointment scheduled for patient {appointment.patient_id}",
            entity_type="appointment",
            entity_id=appointment.id,
        )
        return AppointmentResponse.model_validate(appointment)

    async def get_by_id(self, appointment_id: UUID) -> AppointmentResponse:
        appointment = await self.repository.get_by_id(appointment_id)
        if appointment is None:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        return AppointmentResponse.model_validate(appointment)

    async def list(
        self,
        params: PaginationParams,
        filters: AppointmentFilter | None = None,
        order_by: str | None = None,
    ) -> Page[AppointmentResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[AppointmentResponse.model_validate(a) for a in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, appointment_id: UUID, data: AppointmentUpdate) -> AppointmentResponse:
        appointment = await self.repository.get_by_id(appointment_id)
        if appointment is None:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        updated = await self.repository.update(appointment, data)
        return AppointmentResponse.model_validate(updated)

    async def delete(self, appointment_id: UUID, hard: bool = False) -> None:
        deleted = await self.repository.delete(appointment_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Appointment {appointment_id} not found")

    async def restore(self, appointment_id: UUID) -> AppointmentResponse:
        appointment = await self.repository.restore(appointment_id)
        if appointment is None:
            raise NotFoundException(f"Appointment {appointment_id} not found or not deleted")
        return AppointmentResponse.model_validate(appointment)
