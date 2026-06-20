from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement, or_

from app.billing.model import Invoice, InvoiceItem, Payment
from app.billing.schema import (
    InvoiceCreate,
    InvoiceFilter,
    InvoiceItemCreate,
    InvoiceItemFilter,
    InvoiceItemUpdate,
    InvoiceUpdate,
    PaymentCreate,
    PaymentFilter,
    PaymentUpdate,
)
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context
from core.repositories.tenant_repository import TenantRepository


class InvoiceRepository(TenantRepository[Invoice, InvoiceCreate, InvoiceUpdate, InvoiceFilter]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            Invoice,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "invoice_date": Invoice.invoice_date.asc(),
        "-invoice_date": Invoice.invoice_date.desc(),
        "invoice_number": Invoice.invoice_number.asc(),
        "-invoice_number": Invoice.invoice_number.desc(),
        "created_on": Invoice.created_on.asc(),
        "-created_on": Invoice.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return [selectinload(Invoice.items)]

    def build_filter_conditions(self, filters: InvoiceFilter | None) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.patient_id:
            conditions.append(self.model.patient_id == filters.patient_id)
        if filters.status:
            conditions.append(self.model.status == filters.status)
        if filters.invoice_date_from:
            conditions.append(self.model.invoice_date >= filters.invoice_date_from)
        if filters.invoice_date_to:
            conditions.append(self.model.invoice_date <= filters.invoice_date_to)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.invoice_number.ilike(pattern),
                    self.model.notes.ilike(pattern),
                )
            )
        return conditions


class InvoiceItemRepository(
    TenantRepository[InvoiceItem, InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemFilter]
):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(InvoiceItem, session=session, organization_id=tenant.organization_id)

    ORDER_BY_MAP = {
        "description": InvoiceItem.description.asc(),
        "-description": InvoiceItem.description.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(
        self, filters: InvoiceItemFilter | None
    ) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.invoice_id:
            conditions.append(self.model.invoice_id == filters.invoice_id)
        if filters.search:
            conditions.append(self.model.description.ilike(f"%{filters.search}%"))
        return conditions

    async def get_by_id_for_invoice(self, item_id: UUID, invoice_id: UUID) -> InvoiceItem | None:
        query = self._base_query().where(
            self.model.id == item_id,
            self.model.invoice_id == invoice_id,
            self.model.organization_id == self.organization_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class PaymentRepository(TenantRepository[Payment, PaymentCreate, PaymentUpdate, PaymentFilter]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        super().__init__(
            Payment,
            session=session,
            organization_id=tenant.organization_id,
            clinic_id=tenant.clinic_id,
            clinic_ids=tenant.clinic_ids,
        )

    ORDER_BY_MAP = {
        "payment_date": Payment.payment_date.asc(),
        "-payment_date": Payment.payment_date.desc(),
        "amount": Payment.amount.asc(),
        "-amount": Payment.amount.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(self, filters: PaymentFilter | None) -> list[ColumnElement[bool]]:
        conditions = super().build_filter_conditions(filters)
        if not filters:
            return conditions
        if filters.clinic_id:
            conditions.append(self.model.clinic_id == filters.clinic_id)
        if filters.patient_id:
            conditions.append(self.model.patient_id == filters.patient_id)
        if filters.invoice_id:
            conditions.append(self.model.invoice_id == filters.invoice_id)
        if filters.method:
            conditions.append(self.model.method == filters.method)
        if filters.payment_date_from:
            conditions.append(self.model.payment_date >= filters.payment_date_from)
        if filters.payment_date_to:
            conditions.append(self.model.payment_date <= filters.payment_date_to)
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    self.model.reference.ilike(pattern),
                    self.model.notes.ilike(pattern),
                )
            )
        return conditions
