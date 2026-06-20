from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.documents.model import Notification
from app.notifications.schema import NotificationCreate, NotificationFilter, NotificationUpdate
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class NotificationRepository(
    TenantRepository[Notification, NotificationCreate, NotificationUpdate, NotificationFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(Notification, session=session, organization_id=tenant.organization_id)
        self.tenant = tenant

    ORDER_BY_MAP = {
        "created_on": Notification.created_on.asc(),
        "-created_on": Notification.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: NotificationFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.user_id:
            conditions.append(self.model.user_id == filters.user_id)
        if filters.notification_type:
            conditions.append(self.model.notification_type == filters.notification_type)
        if filters.is_read is not None:
            conditions.append(self.model.is_read == filters.is_read)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.title.ilike(pattern),
                    self.model.message.ilike(pattern),
                )
            )
        return conditions

    async def mark_all_read(self, user_id: UUID) -> int:
        from sqlalchemy import update

        stmt = (
            update(Notification)
            .where(
                Notification.organization_id == self.organization_id,
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                Notification.deleted_on.is_(None),
            )
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
