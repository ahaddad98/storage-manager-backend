from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.clinics.model import Clinic, ClinicRoom
from app.clinics.schema import (
    ClinicCreate,
    ClinicFilter,
    ClinicRoomCreate,
    ClinicRoomFilter,
    ClinicRoomUpdate,
    ClinicUpdate,
)
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class ClinicRepository(TenantRepository[Clinic, ClinicCreate, ClinicUpdate, ClinicFilter]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            Clinic,
            session=session,
            organization_id=tenant.organization_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "name": Clinic.name.asc(),
        "-name": Clinic.name.desc(),
        "city": Clinic.city.asc(),
        "-city": Clinic.city.desc(),
        "created_on": Clinic.created_on.asc(),
        "-created_on": Clinic.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return [selectinload(Clinic.rooms)]

    def build_filter_conditions(self, filters: ClinicFilter | None) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.name.ilike(pattern),
                    self.model.city.ilike(pattern),
                    self.model.address.ilike(pattern),
                )
            )
        if filters.name:
            conditions.append(self.model.name.ilike(f"%{filters.name}%"))
        if filters.city:
            conditions.append(self.model.city.ilike(f"%{filters.city}%"))
        if filters.status:
            conditions.append(self.model.status == filters.status)
        return conditions


class ClinicRoomRepository(
    TenantRepository[ClinicRoom, ClinicRoomCreate, ClinicRoomUpdate, ClinicRoomFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            ClinicRoom,
            session=session,
            organization_id=tenant.organization_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "name": ClinicRoom.name.asc(),
        "-name": ClinicRoom.name.desc(),
        "chair_number": ClinicRoom.chair_number.asc(),
        "-chair_number": ClinicRoom.chair_number.desc(),
        "created_on": ClinicRoom.created_on.asc(),
        "-created_on": ClinicRoom.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: ClinicRoomFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.name.ilike(pattern),
                    self.model.notes.ilike(pattern),
                )
            )
        if filters.name:
            conditions.append(self.model.name.ilike(f"%{filters.name}%"))
        if filters.status:
            conditions.append(self.model.status == filters.status)
        return conditions

    async def get_by_id_for_clinic(self, room_id: UUID, clinic_id: UUID) -> ClinicRoom | None:
        query = self._base_query().where(
            self.model.id == room_id,
            self.model.clinic_id == clinic_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
