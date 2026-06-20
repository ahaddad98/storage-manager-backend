from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.items.repository import ItemRepository
from app.items.schema import ItemCreate, ItemFilter, ItemResponse, ItemUpdate
from app.items.service import ItemService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission
from core.utils.pagination import Page, PaginationParams

router = APIRouter()


def get_item_service(repository: Annotated[ItemRepository, Depends()]) -> ItemService:
    return ItemService(repository)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    _user: Annotated[dict, Depends(require_permission(Permission.ITEMS_WRITE))],
    service: Annotated[ItemService, Depends(get_item_service)],
) -> ItemResponse:
    return await service.create(data)


@router.get("", response_model=Page[ItemResponse])
async def list_items(
    _user: Annotated[dict, Depends(require_permission(Permission.ITEMS_READ))],
    service: Annotated[ItemService, Depends(get_item_service)],
    params: Annotated[PaginationParams, Depends()],
    name: str | None = Query(default=None),
    order_by: str | None = Query(default=None),
) -> Page[ItemResponse]:
    filters = ItemFilter(name=name) if name else None
    return await service.list(params=params, filters=filters, order_by=order_by)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.ITEMS_READ))],
    service: Annotated[ItemService, Depends(get_item_service)],
) -> ItemResponse:
    return await service.get_by_id(item_id)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.ITEMS_WRITE))],
    service: Annotated[ItemService, Depends(get_item_service)],
) -> ItemResponse:
    return await service.update(item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.ITEMS_DELETE))],
    service: Annotated[ItemService, Depends(get_item_service)],
    hard: bool = Query(default=False),
) -> None:
    await service.delete(item_id, hard=hard)


@router.post("/{item_id}/restore", response_model=ItemResponse)
async def restore_item(
    item_id: UUID,
    _user: Annotated[dict, Depends(require_permission(Permission.ITEMS_WRITE))],
    service: Annotated[ItemService, Depends(get_item_service)],
) -> ItemResponse:
    return await service.restore(item_id)
