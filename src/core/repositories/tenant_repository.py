from __future__ import annotations

from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Select, false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from core.models.base import BaseModel as DBBaseModel
from core.repositories.base_repository import Repository

CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)
FilterT = TypeVar("FilterT", bound=BaseModel)
ModelT = TypeVar("ModelT", bound=DBBaseModel)


class TenantRepository(Repository, Generic[ModelT, CreateT, UpdateT, FilterT]):
    """Repository with organization-level tenant isolation."""

    def __init__(
        self,
        model: Type[ModelT],
        session: AsyncSession,
        organization_id: UUID,
        clinic_id: UUID | None = None,
        clinic_ids: set[UUID] | None = None,
    ):
        super().__init__(model, session)
        self.organization_id = organization_id
        self.clinic_id = clinic_id
        self.clinic_ids = clinic_ids

    def build_filter_conditions(self, filters: FilterT | None) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if hasattr(self.model, "organization_id"):
            conditions.append(self.model.organization_id == self.organization_id)
        if hasattr(self.model, "clinic_id"):
            if self.clinic_id:
                conditions.append(self.model.clinic_id == self.clinic_id)
            elif self.clinic_ids is not None:
                if self.clinic_ids:
                    conditions.append(self.model.clinic_id.in_(self.clinic_ids))
                else:
                    conditions.append(false())
        elif (
            getattr(self.model, "__tablename__", None) == "clinics" and self.clinic_ids is not None
        ):
            if self.clinic_ids:
                conditions.append(self.model.id.in_(self.clinic_ids))
            else:
                conditions.append(false())
        if filters:
            conditions.extend(super().build_filter_conditions(filters))
        return conditions

    def _apply_filters(self, query: Select, filters: FilterT | None) -> Select:
        conditions = self.build_filter_conditions(filters)
        if conditions:
            query = query.where(*conditions)
        return query

    async def get_by_id(self, obj_id: UUID, include_deleted: bool = False) -> ModelT | None:
        query = self._base_query(include_deleted=include_deleted).where(self.model.id == obj_id)
        conditions = self.build_filter_conditions(None)
        if conditions:
            query = query.where(*conditions)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, obj_in: CreateT, **extra: Any) -> ModelT:
        data = {**obj_in.model_dump(), **extra}
        if hasattr(self.model, "organization_id"):
            data.setdefault("organization_id", self.organization_id)
        if self.clinic_id and hasattr(self.model, "clinic_id") and "clinic_id" not in data:
            data.setdefault("clinic_id", self.clinic_id)
        db_obj = self.model(**data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
