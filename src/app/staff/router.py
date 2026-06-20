from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.staff.repository import ClinicAssignmentRepository, MembershipRepository
from app.staff.schema import (
    ClinicAssignmentCreate,
    ClinicAssignmentResponse,
    MembershipFilter,
    MembershipResponse,
    MembershipUpdate,
)
from app.staff.service import StaffService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_staff_service(
    membership_repository: Annotated[MembershipRepository, Depends()],
    assignment_repository: Annotated[ClinicAssignmentRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> StaffService:
    return StaffService(membership_repository, assignment_repository, tenant)


@router.get("/memberships", response_model=Page[MembershipResponse])
async def list_memberships(
    _user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[StaffService, Depends(get_staff_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    status: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[MembershipResponse]:
    filters = MembershipFilter(search=search, role=role, status=status)
    if not any([search, role, status]):
        filters = None
    return await service.list_memberships(params=params, filters=filters, order_by=order_by)


@router.get("/memberships/{membership_id}", response_model=MembershipResponse)
async def get_membership(
    membership_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[StaffService, Depends(get_staff_service)],
) -> MembershipResponse:
    return await service.get_membership(membership_id)


@router.patch("/memberships/{membership_id}", response_model=MembershipResponse)
async def update_membership(
    membership_id: UUID,
    data: MembershipUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[StaffService, Depends(get_staff_service)],
) -> MembershipResponse:
    return await service.update_membership(membership_id, data)


@router.get(
    "/memberships/{membership_id}/clinic-assignments",
    response_model=list[ClinicAssignmentResponse],
)
async def list_clinic_assignments(
    membership_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[StaffService, Depends(get_staff_service)],
) -> list[ClinicAssignmentResponse]:
    return await service.list_clinic_assignments(membership_id)


@router.post(
    "/memberships/{membership_id}/clinic-assignments",
    response_model=ClinicAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_clinic(
    membership_id: UUID,
    data: ClinicAssignmentCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[StaffService, Depends(get_staff_service)],
) -> ClinicAssignmentResponse:
    return await service.assign_clinic(membership_id, data)


@router.delete(
    "/memberships/{membership_id}/clinic-assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_clinic_assignment(
    membership_id: UUID,
    assignment_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.STAFF_MANAGE))],
    service: Annotated[StaffService, Depends(get_staff_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.remove_clinic_assignment(membership_id, assignment_id, hard=hard)
