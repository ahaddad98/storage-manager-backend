from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.organizations.model import Organization
from app.organizations.schema import OrganizationUpdate
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context


class OrganizationRepository:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        self.session = session
        self.organization_id = tenant.organization_id

    async def get_current(self) -> Organization | None:
        query = select(Organization).where(
            Organization.id == self.organization_id,
            Organization.deleted_on.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, org: Organization, data: OrganizationUpdate) -> Organization:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
        await self.session.flush()
        await self.session.refresh(org)
        return org
