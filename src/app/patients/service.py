from uuid import UUID

from app.documents.activity import log_activity
from app.patients.repository import MedicalHistoryRepository, PatientRepository
from app.patients.schema import (
    MedicalHistoryResponse,
    MedicalHistoryUpdate,
    PatientCreate,
    PatientFilter,
    PatientResponse,
    PatientUpdate,
)
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class PatientService:
    def __init__(
        self,
        repository: PatientRepository,
        medical_history_repository: MedicalHistoryRepository,
        tenant: TenantContext,
    ):
        self.repository = repository
        self.medical_history_repository = medical_history_repository
        self.tenant = tenant

    async def create(self, data: PatientCreate) -> PatientResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        patient = await self.repository.create(data, created_by=self.tenant.user_id)
        await log_activity(
            self.repository.session,
            organization_id=self.tenant.organization_id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            user_id=self.tenant.user_id,
            event_type="patient.created",
            description=f"Patient {patient.full_name} created",
            entity_type="patient",
            entity_id=patient.id,
        )
        return PatientResponse.model_validate(patient)

    async def get_by_id(self, patient_id: UUID) -> PatientResponse:
        patient = await self.repository.get_by_id(patient_id)
        if patient is None:
            raise NotFoundException(f"Patient {patient_id} not found")
        return PatientResponse.model_validate(patient)

    async def list(
        self,
        params: PaginationParams,
        filters: PatientFilter | None = None,
        order_by: str | None = None,
    ) -> Page[PatientResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[PatientResponse.model_validate(p) for p in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, patient_id: UUID, data: PatientUpdate) -> PatientResponse:
        patient = await self.repository.get_by_id(patient_id)
        if patient is None:
            raise NotFoundException(f"Patient {patient_id} not found")
        updated = await self.repository.update(patient, data)
        return PatientResponse.model_validate(updated)

    async def delete(self, patient_id: UUID, hard: bool = False) -> None:
        deleted = await self.repository.delete(patient_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Patient {patient_id} not found")

    async def restore(self, patient_id: UUID) -> PatientResponse:
        patient = await self.repository.restore(patient_id)
        if patient is None:
            raise NotFoundException(f"Patient {patient_id} not found or not deleted")
        return PatientResponse.model_validate(patient)

    async def get_medical_history(self, patient_id: UUID) -> MedicalHistoryResponse:
        patient = await self.repository.get_by_id(patient_id)
        if patient is None:
            raise NotFoundException(f"Patient {patient_id} not found")
        history = await self.medical_history_repository.get_by_patient_id(patient_id)
        if history is None:
            raise NotFoundException(f"Medical history for patient {patient_id} not found")
        return MedicalHistoryResponse.model_validate(history)

    async def upsert_medical_history(
        self, patient_id: UUID, data: MedicalHistoryUpdate
    ) -> MedicalHistoryResponse:
        patient = await self.repository.get_by_id(patient_id)
        if patient is None:
            raise NotFoundException(f"Patient {patient_id} not found")
        history = await self.medical_history_repository.upsert_for_patient(patient_id, data)
        return MedicalHistoryResponse.model_validate(history)
