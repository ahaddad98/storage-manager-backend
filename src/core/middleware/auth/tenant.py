from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinics.model import Clinic
from app.organizations.model import Organization
from app.staff.model import ClinicAssignment, Membership
from core.business_modules import resolve_enabled_modules
from core.database.session import get_db_session
from core.middleware.auth.exceptions import get_current_user
from core.middleware.auth.permission_list import Role


class TenantContext:
    def __init__(
        self,
        user_id: UUID,
        organization_id: UUID,
        role: str,
        clinic_id: UUID | None = None,
        membership_id: UUID | None = None,
        clinic_ids: set[UUID] | None = None,
        business_type: str = "dental_clinic",
        enabled_modules: list[str] | None = None,
    ):
        self.user_id = user_id
        self.organization_id = organization_id
        self.role = role
        self.clinic_id = clinic_id
        self.membership_id = membership_id
        self.clinic_ids = clinic_ids or set()
        self.business_type = business_type
        self.enabled_modules = enabled_modules or []

    def can_access_clinic(self, clinic_id: UUID | None) -> bool:
        if clinic_id is None:
            return True
        return clinic_id in self.clinic_ids

    def require_clinic_access(self, clinic_id: UUID | None) -> None:
        if self.can_access_clinic(clinic_id):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinic access denied",
        )

    def has_module(self, module_key: str) -> bool:
        return module_key in self.enabled_modules


async def get_tenant_context(
    user: dict[str, Any] = Depends(get_current_user),
    scoped_clinic_id: UUID | None = Query(default=None, alias="clinic_id"),
    session: AsyncSession = Depends(get_db_session),
) -> TenantContext:
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization context",
        )
    user_id = UUID(user["sub"])
    organization_id = UUID(org_id)

    membership_result = await session.execute(
        select(Membership, Organization)
        .join(Organization, Membership.organization_id == Organization.id)
        .where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
            Membership.status == "active",
        )
    )
    row = membership_result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active organization membership",
        )
    membership, organization = row

    if membership.role in {Role.OWNER, Role.ADMIN}:
        clinic_result = await session.execute(
            select(Clinic.id).where(
                Clinic.organization_id == organization_id,
                Clinic.deleted_on.is_(None),
            )
        )
    else:
        clinic_result = await session.execute(
            select(ClinicAssignment.clinic_id)
            .join(Clinic, ClinicAssignment.clinic_id == Clinic.id)
            .where(
                ClinicAssignment.membership_id == membership.id,
                ClinicAssignment.organization_id == organization_id,
                Clinic.organization_id == organization_id,
                Clinic.deleted_on.is_(None),
            )
        )
    clinic_ids = set(clinic_result.scalars().all())
    if scoped_clinic_id and scoped_clinic_id not in clinic_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinic access denied",
        )

    return TenantContext(
        user_id=user_id,
        organization_id=organization_id,
        role=membership.role,
        clinic_id=scoped_clinic_id,
        membership_id=membership.id,
        clinic_ids=clinic_ids,
        business_type=organization.business_type,
        enabled_modules=resolve_enabled_modules(
            organization.business_type,
            organization.enabled_modules,
        ),
    )
