from uuid import UUID

from app.items.repository import ItemRepository
from app.items.schema import ItemCreate, ItemFilter, ItemResponse, ItemUpdate
from core.exceptions import NotFoundException
from core.utils.pagination import Page, PaginationParams


class ItemService:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    async def create(self, data: ItemCreate) -> ItemResponse:
        item = await self.repository.create(data)
        return ItemResponse.model_validate(item)

    async def get_by_id(self, item_id: UUID) -> ItemResponse:
        item = await self.repository.get_by_id(item_id)
        if item is None:
            raise NotFoundException(f"Item {item_id} not found")
        return ItemResponse.model_validate(item)

    async def list(
        self,
        params: PaginationParams,
        filters: ItemFilter | None = None,
        order_by: str | None = None,
    ) -> Page[ItemResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[ItemResponse.model_validate(item) for item in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, item_id: UUID, data: ItemUpdate) -> ItemResponse:
        item = await self.repository.get_by_id(item_id)
        if item is None:
            raise NotFoundException(f"Item {item_id} not found")
        updated = await self.repository.update(item, data)
        return ItemResponse.model_validate(updated)

    async def delete(self, item_id: UUID, hard: bool = False) -> None:
        deleted = await self.repository.delete(item_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Item {item_id} not found")

    async def restore(self, item_id: UUID) -> ItemResponse:
        item = await self.repository.restore(item_id)
        if item is None:
            raise NotFoundException(f"Item {item_id} not found or not deleted")
        return ItemResponse.model_validate(item)
