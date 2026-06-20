from uuid import UUID

from app.notifications.repository import NotificationRepository
from app.notifications.schema import (
    NotificationCreate,
    NotificationFilter,
    NotificationResponse,
    NotificationUpdate,
)
from core.exceptions import ForbiddenException, NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class NotificationService:
    def __init__(self, repository: NotificationRepository, tenant: TenantContext):
        self.repository = repository
        self.tenant = tenant

    async def create(self, data: NotificationCreate) -> NotificationResponse:
        notification = await self.repository.create(data)
        return NotificationResponse.model_validate(notification)

    async def get_by_id(self, notification_id: UUID) -> NotificationResponse:
        notification = await self.repository.get_by_id(notification_id)
        if notification is None:
            raise NotFoundException(f"Notification {notification_id} not found")
        if notification.user_id != self.tenant.user_id:
            raise ForbiddenException("Cannot access another user's notification")
        return NotificationResponse.model_validate(notification)

    async def list(
        self,
        params: PaginationParams,
        filters: NotificationFilter | None = None,
        order_by: str | None = None,
    ) -> Page[NotificationResponse]:
        effective_filters = filters or NotificationFilter()
        effective_filters.user_id = self.tenant.user_id
        page = await self.repository.list(
            params=params, filters=effective_filters, order_by=order_by or "-created_on"
        )
        return Page.create(
            items=[NotificationResponse.model_validate(n) for n in page.items],
            total=page.total,
            params=params,
        )

    async def mark_read(self, notification_id: UUID) -> NotificationResponse:
        notification = await self.repository.get_by_id(notification_id)
        if notification is None:
            raise NotFoundException(f"Notification {notification_id} not found")
        if notification.user_id != self.tenant.user_id:
            raise ForbiddenException("Cannot modify another user's notification")
        updated = await self.repository.update(notification, NotificationUpdate(is_read=True))
        return NotificationResponse.model_validate(updated)

    async def mark_all_read(self) -> dict[str, int]:
        count = await self.repository.mark_all_read(self.tenant.user_id)
        return {"updated": count}

    async def delete(self, notification_id: UUID, hard: bool = False) -> None:
        notification = await self.repository.get_by_id(notification_id)
        if notification is None:
            raise NotFoundException(f"Notification {notification_id} not found")
        if notification.user_id != self.tenant.user_id:
            raise ForbiddenException("Cannot delete another user's notification")
        await self.repository.delete(notification_id, hard=hard)
