from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.reports.repository import ReportRepository
from app.reports.schema import (
    AppointmentReportResponse,
    DashboardStatsResponse,
    PatientReportResponse,
    ReportDateFilter,
    RevenueReportResponse,
)
from app.reports.service import ReportService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission

router = APIRouter()


def get_report_service(
    repository: Annotated[ReportRepository, Depends()],
) -> ReportService:
    return ReportService(repository)


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    _user: Annotated[dict, Depends(require_permission(Permission.REPORTS_VIEW))],
    service: Annotated[ReportService, Depends(get_report_service)],
    clinic_id: UUID | None = Query(default=None),
) -> DashboardStatsResponse:
    filters = ReportDateFilter(clinic_id=clinic_id) if clinic_id else None
    return await service.get_dashboard(filters)


@router.get("/revenue", response_model=RevenueReportResponse)
async def get_revenue_report(
    _user: Annotated[dict, Depends(require_permission(Permission.REPORTS_VIEW))],
    service: Annotated[ReportService, Depends(get_report_service)],
    clinic_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> RevenueReportResponse:
    filters = ReportDateFilter(clinic_id=clinic_id, date_from=date_from, date_to=date_to)
    if not any([clinic_id, date_from, date_to]):
        filters = None
    return await service.get_revenue_report(filters)


@router.get("/appointments", response_model=AppointmentReportResponse)
async def get_appointments_report(
    _user: Annotated[dict, Depends(require_permission(Permission.REPORTS_VIEW))],
    service: Annotated[ReportService, Depends(get_report_service)],
    clinic_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> AppointmentReportResponse:
    filters = ReportDateFilter(clinic_id=clinic_id, date_from=date_from, date_to=date_to)
    if not any([clinic_id, date_from, date_to]):
        filters = None
    return await service.get_appointments_report(filters)


@router.get("/patients", response_model=PatientReportResponse)
async def get_patients_report(
    _user: Annotated[dict, Depends(require_permission(Permission.REPORTS_VIEW))],
    service: Annotated[ReportService, Depends(get_report_service)],
    clinic_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> PatientReportResponse:
    filters = ReportDateFilter(clinic_id=clinic_id, date_from=date_from, date_to=date_to)
    if not any([clinic_id, date_from, date_to]):
        filters = None
    return await service.get_patients_report(filters)
