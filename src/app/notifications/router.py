from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.notifications.repository import NotificationRepository
from app.notifications.schema import NotificationFilter, NotificationResponse
from app.notifications.service import NotificationService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_notification_service(
    repository: Annotated[NotificationRepository, Depends()],
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> NotificationService:
    return NotificationService(repository, tenant)


@router.get("", response_model=Page[NotificationResponse])
async def list_notifications(
    _user: Annotated[dict, Depends(require_permission(Permission.NOTIFICATIONS_READ))],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    params: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    notification_type: str | None = Query(default=None),
    is_read: bool | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[NotificationResponse]:
    filters = NotificationFilter(
        search=search,
        notification_type=notification_type,
        is_read=is_read,
    )
    if not any([search, notification_type, is_read is not None]):
        filters = None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.NOTIFICATIONS_READ))],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> NotificationResponse:
    return await service.get_by_id(notification_id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.NOTIFICATIONS_MANAGE))],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> NotificationResponse:
    return await service.mark_read(notification_id)


@router.post("/read-all")
async def mark_all_notifications_read(
    _user: Annotated[dict, Depends(require_permission(Permission.NOTIFICATIONS_MANAGE))],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> dict[str, int]:
    return await service.mark_all_read()


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.NOTIFICATIONS_MANAGE))],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(notification_id, hard=hard)
