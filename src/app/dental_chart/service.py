from uuid import UUID

from app.dental_chart.repository import DentalChartRepository, ToothRecordRepository
from app.dental_chart.schema import (
    DentalChartCreate,
    DentalChartFilter,
    DentalChartResponse,
    DentalChartUpdate,
    ToothRecordCreate,
    ToothRecordFilter,
    ToothRecordResponse,
    ToothRecordUpdate,
)
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class DentalChartService:
    def __init__(
        self,
        repository: DentalChartRepository,
        tooth_repository: ToothRecordRepository,
        tenant: TenantContext,
    ):
        self.repository = repository
        self.tooth_repository = tooth_repository
        self.tenant = tenant

    async def create(self, data: DentalChartCreate) -> DentalChartResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        chart = await self.repository.create(data)
        return DentalChartResponse.model_validate(chart)

    async def get_by_id(self, chart_id: UUID) -> DentalChartResponse:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        return DentalChartResponse.model_validate(chart)

    async def get_by_patient_id(self, patient_id: UUID) -> DentalChartResponse:
        chart = await self.repository.get_by_patient_id(patient_id)
        if chart is None:
            raise NotFoundException(f"Dental chart for patient {patient_id} not found")
        return DentalChartResponse.model_validate(chart)

    async def list(
        self,
        params: PaginationParams,
        filters: DentalChartFilter | None = None,
        order_by: str | None = None,
    ) -> Page[DentalChartResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[DentalChartResponse.model_validate(c) for c in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, chart_id: UUID, data: DentalChartUpdate) -> DentalChartResponse:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        updated = await self.repository.update(chart, data)
        return DentalChartResponse.model_validate(updated)

    async def delete(self, chart_id: UUID, hard: bool = False) -> None:
        deleted = await self.repository.delete(chart_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Dental chart {chart_id} not found")

    async def create_tooth(self, chart_id: UUID, data: ToothRecordCreate) -> ToothRecordResponse:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        tooth = await self.tooth_repository.create(data, chart_id=chart_id)
        return ToothRecordResponse.model_validate(tooth)

    async def list_teeth(
        self,
        chart_id: UUID,
        params: PaginationParams,
        filters: ToothRecordFilter | None = None,
        order_by: str | None = None,
    ) -> Page[ToothRecordResponse]:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        tooth_filters = filters or ToothRecordFilter()
        tooth_filters.chart_id = chart_id
        page = await self.tooth_repository.list(
            params=params, filters=tooth_filters, order_by=order_by
        )
        return Page.create(
            items=[ToothRecordResponse.model_validate(t) for t in page.items],
            total=page.total,
            params=params,
        )

    async def get_tooth(self, chart_id: UUID, tooth_id: UUID) -> ToothRecordResponse:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        tooth = await self.tooth_repository.get_by_id_for_chart(tooth_id, chart_id)
        if tooth is None:
            raise NotFoundException(f"Tooth record {tooth_id} not found in chart {chart_id}")
        return ToothRecordResponse.model_validate(tooth)

    async def update_tooth(
        self, chart_id: UUID, tooth_id: UUID, data: ToothRecordUpdate
    ) -> ToothRecordResponse:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        tooth = await self.tooth_repository.get_by_id_for_chart(tooth_id, chart_id)
        if tooth is None:
            raise NotFoundException(f"Tooth record {tooth_id} not found in chart {chart_id}")
        updated = await self.tooth_repository.update(tooth, data)
        return ToothRecordResponse.model_validate(updated)

    async def delete_tooth(self, chart_id: UUID, tooth_id: UUID, hard: bool = False) -> None:
        chart = await self.repository.get_by_id(chart_id)
        if chart is None:
            raise NotFoundException(f"Dental chart {chart_id} not found")
        tooth = await self.tooth_repository.get_by_id_for_chart(tooth_id, chart_id)
        if tooth is None:
            raise NotFoundException(f"Tooth record {tooth_id} not found in chart {chart_id}")
        await self.tooth_repository.delete(tooth_id, hard=hard)
