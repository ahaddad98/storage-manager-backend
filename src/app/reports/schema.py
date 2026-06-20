from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ReportDateFilter(BaseModel):
    clinic_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None


class DashboardStatsResponse(BaseModel):
    total_patients: int
    active_patients: int
    appointments_today: int
    appointments_this_week: int
    pending_appointments: int
    total_revenue: Decimal
    revenue_this_month: Decimal
    unpaid_invoices: int
    low_stock_items: int
    new_patients_this_month: int


class RevenueReportItem(BaseModel):
    period: str
    invoice_count: int
    total_invoiced: Decimal
    total_collected: Decimal
    outstanding: Decimal


class RevenueReportResponse(BaseModel):
    items: list[RevenueReportItem]
    total_invoiced: Decimal
    total_collected: Decimal
    total_outstanding: Decimal


class AppointmentReportItem(BaseModel):
    period: str
    total: int
    completed: int
    cancelled: int
    no_show: int


class AppointmentReportResponse(BaseModel):
    items: list[AppointmentReportItem]
    total_appointments: int
    completion_rate: float


class PatientReportItem(BaseModel):
    period: str
    new_patients: int
    active_patients: int


class PatientReportResponse(BaseModel):
    items: list[PatientReportItem]
    total_patients: int
    new_patients: int
    growth_rate: float
