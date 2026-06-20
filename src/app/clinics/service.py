from uuid import UUID

from app.clinics.repository import ClinicRepository, ClinicRoomRepository
from app.clinics.schema import (
    ClinicCreate,
    ClinicFilter,
    ClinicResponse,
    ClinicRoomCreate,
    ClinicRoomFilter,
    ClinicRoomResponse,
    ClinicRoomUpdate,
    ClinicUpdate,
)
from app.staff.repository import ClinicAssignmentRepository, MembershipRepository
from app.staff.schema import ClinicAssignmentCreate
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class ClinicService:
    def __init__(
        self,
        repository: ClinicRepository,
        room_repository: ClinicRoomRepository,
        membership_repository: MembershipRepository,
        assignment_repository: ClinicAssignmentRepository,
        tenant: TenantContext,
    ):
        self.repository = repository
        self.room_repository = room_repository
        self.membership_repository = membership_repository
        self.assignment_repository = assignment_repository
        self.tenant = tenant

    async def create(self, data: ClinicCreate) -> ClinicResponse:
        clinic = await self.repository.create(data)
        membership = await self.membership_repository.get_active_by_user_id(self.tenant.user_id)
        if membership:
            existing = await self.assignment_repository.get_by_membership_and_clinic(
                membership.id, clinic.id
            )
            if existing is None:
                await self.assignment_repository.create(
                    ClinicAssignmentCreate(clinic_id=clinic.id),
                    membership_id=membership.id,
                )
        return ClinicResponse.model_validate(clinic)

    async def get_by_id(self, clinic_id: UUID) -> ClinicResponse:
        self.tenant.require_clinic_access(clinic_id)
        clinic = await self.repository.get_by_id(clinic_id)
        if clinic is None:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        return ClinicResponse.model_validate(clinic)

    async def list(
        self,
        params: PaginationParams,
        filters: ClinicFilter | None = None,
        order_by: str | None = None,
    ) -> Page[ClinicResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[ClinicResponse.model_validate(c) for c in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, clinic_id: UUID, data: ClinicUpdate) -> ClinicResponse:
        self.tenant.require_clinic_access(clinic_id)
        clinic = await self.repository.get_by_id(clinic_id)
        if clinic is None:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        updated = await self.repository.update(clinic, data)
        return ClinicResponse.model_validate(updated)

    async def delete(self, clinic_id: UUID, hard: bool = False) -> None:
        self.tenant.require_clinic_access(clinic_id)
        deleted = await self.repository.delete(clinic_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Clinic {clinic_id} not found")

    async def restore(self, clinic_id: UUID) -> ClinicResponse:
        self.tenant.require_clinic_access(clinic_id)
        clinic = await self.repository.restore(clinic_id)
        if clinic is None:
            raise NotFoundException(f"Clinic {clinic_id} not found or not deleted")
        return ClinicResponse.model_validate(clinic)

    async def create_room(self, clinic_id: UUID, data: ClinicRoomCreate) -> ClinicRoomResponse:
        self.tenant.require_clinic_access(clinic_id)
        clinic = await self.repository.get_by_id(clinic_id)
        if clinic is None:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        room = await self.room_repository.create(data, clinic_id=clinic_id)
        return ClinicRoomResponse.model_validate(room)

    async def list_rooms(
        self,
        clinic_id: UUID,
        params: PaginationParams,
        filters: ClinicRoomFilter | None = None,
        order_by: str | None = None,
    ) -> Page[ClinicRoomResponse]:
        self.tenant.require_clinic_access(clinic_id)
        clinic = await self.repository.get_by_id(clinic_id)
        if clinic is None:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        room_filters = filters or ClinicRoomFilter()
        room_filters.clinic_id = clinic_id
        page = await self.room_repository.list(
            params=params, filters=room_filters, order_by=order_by
        )
        return Page.create(
            items=[ClinicRoomResponse.model_validate(r) for r in page.items],
            total=page.total,
            params=params,
        )

    async def get_room(self, clinic_id: UUID, room_id: UUID) -> ClinicRoomResponse:
        self.tenant.require_clinic_access(clinic_id)
        room = await self.room_repository.get_by_id_for_clinic(room_id, clinic_id)
        if room is None:
            raise NotFoundException(f"Room {room_id} not found in clinic {clinic_id}")
        return ClinicRoomResponse.model_validate(room)

    async def update_room(
        self, clinic_id: UUID, room_id: UUID, data: ClinicRoomUpdate
    ) -> ClinicRoomResponse:
        self.tenant.require_clinic_access(clinic_id)
        room = await self.room_repository.get_by_id_for_clinic(room_id, clinic_id)
        if room is None:
            raise NotFoundException(f"Room {room_id} not found in clinic {clinic_id}")
        updated = await self.room_repository.update(room, data)
        return ClinicRoomResponse.model_validate(updated)

    async def delete_room(self, clinic_id: UUID, room_id: UUID, hard: bool = False) -> None:
        self.tenant.require_clinic_access(clinic_id)
        room = await self.room_repository.get_by_id_for_clinic(room_id, clinic_id)
        if room is None:
            raise NotFoundException(f"Room {room_id} not found in clinic {clinic_id}")
        await self.room_repository.delete(room_id, hard=hard)

    async def restore_room(self, clinic_id: UUID, room_id: UUID) -> ClinicRoomResponse:
        self.tenant.require_clinic_access(clinic_id)
        room = await self.room_repository.restore(room_id)
        if room is None or room.clinic_id != clinic_id:
            raise NotFoundException(
                f"Room {room_id} not found or not deleted in clinic {clinic_id}"
            )
        return ClinicRoomResponse.model_validate(room)
