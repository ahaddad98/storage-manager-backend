from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import false, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.model import Appointment
from app.billing.model import Invoice, Payment
from app.inventory.model import InventoryItem
from app.patients.model import Patient
from app.reports.schema import ReportDateFilter
from core.database.session import get_db_session
from core.middleware.auth.tenant import TenantContext, get_tenant_context


class ReportRepository:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ):
        self.session = session
        self.organization_id = tenant.organization_id
        self.clinic_id = tenant.clinic_id
        self.clinic_ids = tenant.clinic_ids

    def _clinic_filter(self, model) -> list:
        conditions = [
            model.organization_id == self.organization_id,
            model.deleted_on.is_(None),
        ]
        clinic_id = self.clinic_id
        if clinic_id and hasattr(model, "clinic_id"):
            conditions.append(model.clinic_id == clinic_id)
        elif hasattr(model, "clinic_id"):
            if self.clinic_ids:
                conditions.append(model.clinic_id.in_(self.clinic_ids))
            else:
                conditions.append(false())
        return conditions

    async def count_patients(self, status: str | None = None, clinic_id: UUID | None = None) -> int:
        conditions = self._clinic_filter(Patient)
        if status:
            conditions.append(Patient.status == status)
        if clinic_id:
            conditions.append(Patient.clinic_id == clinic_id)
        query = select(func.count()).select_from(Patient).where(*conditions)
        return (await self.session.execute(query)).scalar_one()

    async def count_new_patients_since(self, since: datetime, clinic_id: UUID | None = None) -> int:
        conditions = self._clinic_filter(Patient)
        conditions.append(Patient.created_on >= since)
        if clinic_id:
            conditions.append(Patient.clinic_id == clinic_id)
        query = select(func.count()).select_from(Patient).where(*conditions)
        return (await self.session.execute(query)).scalar_one()

    async def count_appointments(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        status: str | None = None,
        clinic_id: UUID | None = None,
    ) -> int:
        conditions = self._clinic_filter(Appointment)
        if start:
            conditions.append(Appointment.start_time >= start)
        if end:
            conditions.append(Appointment.start_time <= end)
        if status:
            conditions.append(Appointment.status == status)
        if clinic_id:
            conditions.append(Appointment.clinic_id == clinic_id)
        query = select(func.count()).select_from(Appointment).where(*conditions)
        return (await self.session.execute(query)).scalar_one()

    async def sum_payments(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        clinic_id: UUID | None = None,
    ) -> Decimal:
        conditions = self._clinic_filter(Payment)
        if date_from:
            conditions.append(Payment.payment_date >= date_from)
        if date_to:
            conditions.append(Payment.payment_date <= date_to)
        if clinic_id:
            conditions.append(Payment.clinic_id == clinic_id)
        query = select(func.coalesce(func.sum(Payment.amount), 0)).where(*conditions)
        result = (await self.session.execute(query)).scalar_one()
        return Decimal(str(result))

    async def sum_invoices(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        status: str | None = None,
        clinic_id: UUID | None = None,
    ) -> Decimal:
        conditions = self._clinic_filter(Invoice)
        if date_from:
            conditions.append(Invoice.invoice_date >= date_from)
        if date_to:
            conditions.append(Invoice.invoice_date <= date_to)
        if status:
            conditions.append(Invoice.status == status)
        if clinic_id:
            conditions.append(Invoice.clinic_id == clinic_id)
        query = select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(*conditions)
        result = (await self.session.execute(query)).scalar_one()
        return Decimal(str(result))

    async def count_unpaid_invoices(self, clinic_id: UUID | None = None) -> int:
        conditions = self._clinic_filter(Invoice)
        conditions.append(Invoice.status.in_(["unpaid", "partial"]))
        if clinic_id:
            conditions.append(Invoice.clinic_id == clinic_id)
        query = select(func.count()).select_from(Invoice).where(*conditions)
        return (await self.session.execute(query)).scalar_one()

    async def count_low_stock_items(self, clinic_id: UUID | None = None) -> int:
        conditions = self._clinic_filter(InventoryItem)
        conditions.append(InventoryItem.quantity <= InventoryItem.min_stock_level)
        if clinic_id:
            conditions.append(InventoryItem.clinic_id == clinic_id)
        query = select(func.count()).select_from(InventoryItem).where(*conditions)
        return (await self.session.execute(query)).scalar_one()

    async def revenue_by_month(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        clinic_id: UUID | None = None,
    ) -> list[tuple[str, int, Decimal, Decimal]]:
        conditions = self._clinic_filter(Invoice)
        if date_from:
            conditions.append(Invoice.invoice_date >= date_from)
        if date_to:
            conditions.append(Invoice.invoice_date <= date_to)
        if clinic_id:
            conditions.append(Invoice.clinic_id == clinic_id)
        period = func.to_char(Invoice.invoice_date, "YYYY-MM")
        query = (
            select(
                period.label("period"),
                func.count(Invoice.id).label("invoice_count"),
                func.coalesce(func.sum(Invoice.total_amount), 0).label("total_invoiced"),
                func.coalesce(func.sum(Invoice.amount_paid), 0).label("total_collected"),
            )
            .where(*conditions)
            .group_by(period)
            .order_by(period)
        )
        result = await self.session.execute(query)
        return [
            (
                row.period,
                row.invoice_count,
                Decimal(str(row.total_invoiced)),
                Decimal(str(row.total_collected)),
            )
            for row in result
        ]

    async def appointments_by_month(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        clinic_id: UUID | None = None,
    ) -> list[tuple[str, int, int, int, int]]:
        conditions = self._clinic_filter(Appointment)
        if date_from:
            conditions.append(
                Appointment.start_time
                >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
            )
        if date_to:
            conditions.append(
                Appointment.start_time
                <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)
            )
        if clinic_id:
            conditions.append(Appointment.clinic_id == clinic_id)
        period = func.to_char(Appointment.start_time, "YYYY-MM")
        query = (
            select(
                period.label("period"),
                func.count(Appointment.id).label("total"),
                func.count(Appointment.id)
                .filter(Appointment.status == "completed")
                .label("completed"),
                func.count(Appointment.id)
                .filter(Appointment.status == "cancelled")
                .label("cancelled"),
                func.count(Appointment.id).filter(Appointment.status == "no_show").label("no_show"),
            )
            .where(*conditions)
            .group_by(period)
            .order_by(period)
        )
        result = await self.session.execute(query)
        return [
            (row.period, row.total, row.completed, row.cancelled, row.no_show) for row in result
        ]

    async def patients_by_month(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        clinic_id: UUID | None = None,
    ) -> list[tuple[str, int]]:
        conditions = self._clinic_filter(Patient)
        if date_from:
            conditions.append(
                Patient.created_on
                >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
            )
        if date_to:
            conditions.append(
                Patient.created_on
                <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)
            )
        if clinic_id:
            conditions.append(Patient.clinic_id == clinic_id)
        period = func.to_char(Patient.created_on, "YYYY-MM")
        query = (
            select(period.label("period"), func.count(Patient.id).label("new_patients"))
            .where(*conditions)
            .group_by(period)
            .order_by(period)
        )
        result = await self.session.execute(query)
        return [(row.period, row.new_patients) for row in result]
