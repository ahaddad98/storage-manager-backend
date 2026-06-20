from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement

from app.staff.model import ClinicAssignment, Membership
from app.staff.schema import MembershipFilter, MembershipUpdate
from app.users.model import User
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class MembershipRepository(TenantRepository[Membership, dict, MembershipUpdate, MembershipFilter]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(Membership, session=session, organization_id=tenant.organization_id)

    ORDER_BY_MAP = {
        "role": Membership.role.asc(),
        "-role": Membership.role.desc(),
        "created_on": Membership.created_on.asc(),
        "-created_on": Membership.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return [
            joinedload(Membership.user),
            selectinload(Membership.clinic_assignments),
        ]

    def build_filter_conditions(
        self, filters: MembershipFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.role:
            conditions.append(self.model.role == filters.role)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                self.model.user.has(User.full_name.ilike(pattern))
                | self.model.user.has(User.email.ilike(pattern))
            )
        return conditions

    async def get_active_by_user_id(self, user_id: UUID) -> Membership | None:
        query = self._base_query().where(
            self.model.user_id == user_id,
            self.model.organization_id == self.organization_id,
            self.model.status == "active",
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class ClinicAssignmentRepository(TenantRepository):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(ClinicAssignment, session=session, organization_id=tenant.organization_id)

    async def get_by_membership_and_clinic(
        self, membership_id: UUID, clinic_id: UUID
    ) -> ClinicAssignment | None:
        query = self._base_query().where(
            self.model.membership_id == membership_id,
            self.model.clinic_id == clinic_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_membership(self, membership_id: UUID) -> list[ClinicAssignment]:
        query = self._base_query().where(
            self.model.membership_id == membership_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
