from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, List, Sequence, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement

from core.models.base import BaseModel as DBBaseModel
from core.utils.pagination import Page, PaginationParams

ModelT = TypeVar("ModelT", bound=DBBaseModel)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)
FilterT = TypeVar("FilterT", bound=BaseModel)


class Repository(Generic[ModelT, CreateT, UpdateT, FilterT]):
    model: Type[ModelT]
    ORDER_BY_MAP: dict[str, Any] = {}

    def __init__(self, model: Type[ModelT], session: AsyncSession):
        self.model = model
        self.session = session

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(self, filters: FilterT | None) -> list[ColumnElement[bool]]:
        return []

    def _base_query(self, include_deleted: bool = False) -> Select[tuple[ModelT]]:
        query = select(self.model)
        if not include_deleted and hasattr(self.model, "deleted_on"):
            query = query.where(self.model.deleted_on.is_(None))
        for rel in self.default_relationships():
            query = query.options(rel)
        return query

    def _apply_filters(self, query: Select, filters: FilterT | None) -> Select:
        conditions = self.build_filter_conditions(filters)
        if conditions:
            query = query.where(*conditions)
        return query

    def _apply_ordering(self, query: Select, order_by: str | None) -> Select:
        if order_by and order_by in self.ORDER_BY_MAP:
            return query.order_by(self.ORDER_BY_MAP[order_by])
        if hasattr(self.model, "created_on"):
            return query.order_by(self.model.created_on.desc())
        return query

    async def create(self, obj_in: CreateT) -> ModelT:
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def create_many(self, objs_in: list[CreateT]) -> list[ModelT]:
        db_objs = [self.model(**obj.model_dump()) for obj in objs_in]
        self.session.add_all(db_objs)
        await self.session.flush()
        for obj in db_objs:
            await self.session.refresh(obj)
        return db_objs

    async def get_by_id(self, obj_id: UUID, include_deleted: bool = False) -> ModelT | None:
        query = self._base_query(include_deleted=include_deleted).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, obj_id: UUID) -> ModelT:
        obj = await self.get_by_id(obj_id)
        if obj is None:
            raise ValueError(f"{self.model.__name__} with id {obj_id} not found")
        return obj

    async def get_first(self, filters: FilterT | None = None) -> ModelT | None:
        query = self._apply_filters(self._base_query(), filters)
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def list(
        self,
        params: PaginationParams,
        filters: FilterT | None = None,
        order_by: str | None = None,
    ) -> Page[ModelT]:
        base = self._apply_filters(self._base_query(), filters)
        count_query = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        query = self._apply_ordering(base, order_by)
        query = query.offset(params.skip).limit(params.limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return Page.create(items=items, total=total, params=params)

    async def list_raw(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: FilterT | None = None,
        order_by: str | None = None,
    ) -> List[ModelT]:
        query = self._apply_ordering(self._apply_filters(self._base_query(), filters), order_by)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: FilterT | None = None) -> int:
        base = self._apply_filters(self._base_query(), filters)
        count_query = select(func.count()).select_from(base.subquery())
        return (await self.session.execute(count_query)).scalar_one()

    async def exists(self, filters: FilterT | None = None) -> bool:
        return await self.count(filters) > 0

    async def update(self, obj: ModelT, obj_in: UpdateT) -> ModelT:
        update_data = obj_in.model_dump(exclude_unset=True)
        return await self.update_from_dict(obj, update_data)

    async def update_from_dict(self, obj: ModelT, data: dict[str, Any]) -> ModelT:
        for field, value in data.items():
            setattr(obj, field, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_many(self, ids: List[UUID], data: dict[str, Any]) -> int:
        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .where(self.model.deleted_on.is_(None))
            .values(**data)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return int(getattr(result, "rowcount", 0))

    async def update_with_filter(self, filters: FilterT, data: dict[str, Any]) -> int:
        conditions = self.build_filter_conditions(filters)
        stmt = (
            update(self.model)
            .where(*conditions)
            .where(self.model.deleted_on.is_(None))
            .values(**data)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return int(getattr(result, "rowcount", 0))

    async def delete(self, obj_id: UUID, hard: bool = False) -> bool:
        obj = await self.get_by_id(obj_id)
        if obj is None:
            return False
        if hard:
            await self.session.delete(obj)
        else:
            obj.deleted_on = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def delete_many(self, ids: List[UUID], hard: bool = False) -> int:
        count = 0
        for obj_id in ids:
            if await self.delete(obj_id, hard=hard):
                count += 1
        return count

    async def delete_with_filter(self, filters: FilterT, hard: bool = False) -> int:
        objs = await self.list_raw(filters=filters, limit=10_000)
        count = 0
        for obj in objs:
            if hard:
                await self.session.delete(obj)
            else:
                obj.deleted_on = datetime.now(timezone.utc)
            count += 1
        await self.session.flush()
        return count

    async def restore(self, obj_id: UUID) -> ModelT | None:
        obj = await self.get_by_id(obj_id, include_deleted=True)
        if obj is None or obj.deleted_on is None:
            return None
        obj.deleted_on = None
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def restore_many(self, ids: List[UUID]) -> int:
        count = 0
        for obj_id in ids:
            if await self.restore(obj_id):
                count += 1
        return count
