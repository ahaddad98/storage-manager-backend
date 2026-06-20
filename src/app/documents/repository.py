from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.documents.model import ActivityLog, Document
from app.documents.schema import ActivityLogFilter, DocumentCreate, DocumentFilter, DocumentUpdate
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class DocumentRepository(
    TenantRepository[Document, DocumentCreate, DocumentUpdate, DocumentFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            Document,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "file_name": Document.file_name.asc(),
        "-file_name": Document.file_name.desc(),
        "created_on": Document.created_on.asc(),
        "-created_on": Document.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(self, filters: DocumentFilter | None) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.patient_id:
            conditions.append(self.model.patient_id == filters.patient_id)
        if filters.treatment_id:
            conditions.append(self.model.treatment_id == filters.treatment_id)
        if filters.invoice_id:
            conditions.append(self.model.invoice_id == filters.invoice_id)
        if filters.document_type:
            conditions.append(self.model.document_type == filters.document_type)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.file_name.ilike(pattern),
                    self.model.notes.ilike(pattern),
                )
            )
        return conditions


class ActivityLogRepository(TenantRepository):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            ActivityLog,
            session=session,
            organization_id=tenant.organization_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "created_on": ActivityLog.created_on.asc(),
        "-created_on": ActivityLog.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: ActivityLogFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.patient_id:
            conditions.append(self.model.patient_id == filters.patient_id)
        if filters.user_id:
            conditions.append(self.model.user_id == filters.user_id)
        if filters.event_type:
            conditions.append(self.model.event_type == filters.event_type)
        if filters.search:
            conditions.append(self.model.description.ilike(f"%{filters.search}%"))
        return conditions
