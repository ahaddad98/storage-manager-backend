from uuid import UUID

from app.staff.repository import ClinicAssignmentRepository, MembershipRepository
from app.staff.schema import (
    ClinicAssignmentCreate,
    ClinicAssignmentResponse,
    MembershipFilter,
    MembershipResponse,
    MembershipUpdate,
)
from core.exceptions import ConflictException, NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class StaffService:
    def __init__(
        self,
        membership_repository: MembershipRepository,
        assignment_repository: ClinicAssignmentRepository,
        tenant: TenantContext,
    ):
        self.membership_repository = membership_repository
        self.assignment_repository = assignment_repository
        self.tenant = tenant

    async def get_membership(self, membership_id: UUID) -> MembershipResponse:
        membership = await self.membership_repository.get_by_id(membership_id)
        if membership is None:
            raise NotFoundException(f"Membership {membership_id} not found")
        return MembershipResponse.model_validate(membership)

    async def list_memberships(
        self,
        params: PaginationParams,
        filters: MembershipFilter | None = None,
        order_by: str | None = None,
    ) -> Page[MembershipResponse]:
        page = await self.membership_repository.list(
            params=params, filters=filters, order_by=order_by
        )
        return Page.create(
            items=[MembershipResponse.model_validate(m) for m in page.items],
            total=page.total,
            params=params,
        )

    async def update_membership(
        self, membership_id: UUID, data: MembershipUpdate
    ) -> MembershipResponse:
        membership = await self.membership_repository.get_by_id(membership_id)
        if membership is None:
            raise NotFoundException(f"Membership {membership_id} not found")
        updated = await self.membership_repository.update(membership, data)
        refreshed = await self.membership_repository.get_by_id(membership_id)
        return MembershipResponse.model_validate(refreshed)

    async def assign_clinic(
        self, membership_id: UUID, data: ClinicAssignmentCreate
    ) -> ClinicAssignmentResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        membership = await self.membership_repository.get_by_id(membership_id)
        if membership is None:
            raise NotFoundException(f"Membership {membership_id} not found")
        existing = await self.assignment_repository.get_by_membership_and_clinic(
            membership_id, data.clinic_id
        )
        if existing:
            raise ConflictException(
                f"Membership {membership_id} already assigned to clinic {data.clinic_id}"
            )
        assignment = await self.assignment_repository.create(data, membership_id=membership_id)
        return ClinicAssignmentResponse.model_validate(assignment)

    async def list_clinic_assignments(self, membership_id: UUID) -> list[ClinicAssignmentResponse]:
        membership = await self.membership_repository.get_by_id(membership_id)
        if membership is None:
            raise NotFoundException(f"Membership {membership_id} not found")
        assignments = await self.assignment_repository.list_for_membership(membership_id)
        return [ClinicAssignmentResponse.model_validate(a) for a in assignments]

    async def remove_clinic_assignment(
        self, membership_id: UUID, assignment_id: UUID, hard: bool = False
    ) -> None:
        membership = await self.membership_repository.get_by_id(membership_id)
        if membership is None:
            raise NotFoundException(f"Membership {membership_id} not found")
        assignment = await self.assignment_repository.get_by_id(assignment_id)
        if assignment is None or assignment.membership_id != membership_id:
            raise NotFoundException(
                f"Clinic assignment {assignment_id} not found for membership {membership_id}"
            )
        await self.assignment_repository.delete(assignment_id, hard=hard)
