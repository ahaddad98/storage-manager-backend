from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement

from app.items.model import Item
from app.items.schema import ItemCreate, ItemFilter, ItemUpdate
from core.database.session import get_db_session
from core.repositories.base_repository import Repository


class ItemRepository(Repository[Item, ItemCreate, ItemUpdate, ItemFilter]):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]):
        super().__init__(Item, session=session)

    ORDER_BY_MAP = {
        "name": Item.name.asc(),
        "-name": Item.name.desc(),
        "created_on": Item.created_on.asc(),
        "-created_on": Item.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(self, filters: ItemFilter | None) -> list[ColumnElement[bool]]:
        if not filters:
            return []
        conditions: list[ColumnElement[bool]] = []
        if filters.name:
            conditions.append(self.model.name.ilike(f"%{filters.name}%"))
        return conditions
