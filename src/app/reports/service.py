from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.reports.repository import ReportRepository
from app.reports.schema import (
    AppointmentReportItem,
    AppointmentReportResponse,
    DashboardStatsResponse,
    PatientReportItem,
    PatientReportResponse,
    ReportDateFilter,
    RevenueReportItem,
    RevenueReportResponse,
)


class ReportService:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    def _resolve_clinic_id(self, filters: ReportDateFilter | None):
        if filters and filters.clinic_id:
            return filters.clinic_id
        return self.repository.clinic_id

    async def get_dashboard(
        self, filters: ReportDateFilter | None = None
    ) -> DashboardStatsResponse:
        clinic_id = self._resolve_clinic_id(filters)
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        total_patients = await self.repository.count_patients(clinic_id=clinic_id)
        active_patients = await self.repository.count_patients(status="active", clinic_id=clinic_id)
        appointments_today = await self.repository.count_appointments(
            start=today_start, end=today_end, clinic_id=clinic_id
        )
        appointments_this_week = await self.repository.count_appointments(
            start=week_start, end=today_end, clinic_id=clinic_id
        )
        pending_appointments = await self.repository.count_appointments(
            status="scheduled", clinic_id=clinic_id
        )
        total_revenue = await self.repository.sum_payments(clinic_id=clinic_id)
        revenue_this_month = await self.repository.sum_payments(
            date_from=month_start.date(), clinic_id=clinic_id
        )
        unpaid_invoices = await self.repository.count_unpaid_invoices(clinic_id=clinic_id)
        low_stock_items = await self.repository.count_low_stock_items(clinic_id=clinic_id)
        new_patients_this_month = await self.repository.count_new_patients_since(
            month_start, clinic_id=clinic_id
        )

        return DashboardStatsResponse(
            total_patients=total_patients,
            active_patients=active_patients,
            appointments_today=appointments_today,
            appointments_this_week=appointments_this_week,
            pending_appointments=pending_appointments,
            total_revenue=total_revenue,
            revenue_this_month=revenue_this_month,
            unpaid_invoices=unpaid_invoices,
            low_stock_items=low_stock_items,
            new_patients_this_month=new_patients_this_month,
        )

    async def get_revenue_report(
        self, filters: ReportDateFilter | None = None
    ) -> RevenueReportResponse:
        clinic_id = self._resolve_clinic_id(filters)
        date_from = filters.date_from if filters else None
        date_to = filters.date_to if filters else None
        rows = await self.repository.revenue_by_month(date_from, date_to, clinic_id)
        items = [
            RevenueReportItem(
                period=period,
                invoice_count=count,
                total_invoiced=invoiced,
                total_collected=collected,
                outstanding=invoiced - collected,
            )
            for period, count, invoiced, collected in rows
        ]
        total_invoiced = sum((i.total_invoiced for i in items), Decimal("0"))
        total_collected = sum((i.total_collected for i in items), Decimal("0"))
        return RevenueReportResponse(
            items=items,
            total_invoiced=total_invoiced,
            total_collected=total_collected,
            total_outstanding=total_invoiced - total_collected,
        )

    async def get_appointments_report(
        self, filters: ReportDateFilter | None = None
    ) -> AppointmentReportResponse:
        clinic_id = self._resolve_clinic_id(filters)
        date_from = filters.date_from if filters else None
        date_to = filters.date_to if filters else None
        rows = await self.repository.appointments_by_month(date_from, date_to, clinic_id)
        items = [
            AppointmentReportItem(
                period=period,
                total=total,
                completed=completed,
                cancelled=cancelled,
                no_show=no_show,
            )
            for period, total, completed, cancelled, no_show in rows
        ]
        total_appointments = sum(i.total for i in items)
        completed = sum(i.completed for i in items)
        completion_rate = (completed / total_appointments * 100) if total_appointments else 0.0
        return AppointmentReportResponse(
            items=items,
            total_appointments=total_appointments,
            completion_rate=round(completion_rate, 2),
        )

    async def get_patients_report(
        self, filters: ReportDateFilter | None = None
    ) -> PatientReportResponse:
        clinic_id = self._resolve_clinic_id(filters)
        date_from = filters.date_from if filters else None
        date_to = filters.date_to if filters else None
        rows = await self.repository.patients_by_month(date_from, date_to, clinic_id)
        items = [
            PatientReportItem(period=period, new_patients=new, active_patients=0)
            for period, new in rows
        ]
        new_patients = sum(i.new_patients for i in items)
        total_patients = await self.repository.count_patients(clinic_id=clinic_id)
        growth_rate = (new_patients / total_patients * 100) if total_patients else 0.0
        return PatientReportResponse(
            items=items,
            total_patients=total_patients,
            new_patients=new_patients,
            growth_rate=round(growth_rate, 2),
        )
