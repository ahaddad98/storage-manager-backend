from uuid import UUID

from app.documents.repository import ActivityLogRepository, DocumentRepository
from app.documents.schema import (
    ActivityLogFilter,
    ActivityLogResponse,
    DocumentCreate,
    DocumentFilter,
    DocumentResponse,
    DocumentUpdate,
)
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        activity_log_repository: ActivityLogRepository,
        tenant: TenantContext,
    ):
        self.repository = repository
        self.activity_log_repository = activity_log_repository
        self.tenant = tenant

    async def create(self, data: DocumentCreate) -> DocumentResponse:
        document = await self.repository.create(data, created_by=self.tenant.user_id)
        return DocumentResponse.model_validate(document)

    async def get_by_id(self, document_id: UUID) -> DocumentResponse:
        document = await self.repository.get_by_id(document_id)
        if document is None:
            raise NotFoundException(f"Document {document_id} not found")
        return DocumentResponse.model_validate(document)

    async def list(
        self,
        params: PaginationParams,
        filters: DocumentFilter | None = None,
        order_by: str | None = None,
    ) -> Page[DocumentResponse]:
        page = await self.repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[DocumentResponse.model_validate(d) for d in page.items],
            total=page.total,
            params=params,
        )

    async def update(self, document_id: UUID, data: DocumentUpdate) -> DocumentResponse:
        document = await self.repository.get_by_id(document_id)
        if document is None:
            raise NotFoundException(f"Document {document_id} not found")
        updated = await self.repository.update(document, data)
        return DocumentResponse.model_validate(updated)

    async def delete(self, document_id: UUID, hard: bool = False) -> None:
        deleted = await self.repository.delete(document_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Document {document_id} not found")

    async def restore(self, document_id: UUID) -> DocumentResponse:
        document = await self.repository.restore(document_id)
        if document is None:
            raise NotFoundException(f"Document {document_id} not found or not deleted")
        return DocumentResponse.model_validate(document)

    async def list_activity_logs(
        self,
        params: PaginationParams,
        filters: ActivityLogFilter | None = None,
        order_by: str | None = None,
    ) -> Page[ActivityLogResponse]:
        page = await self.activity_log_repository.list(
            params=params, filters=filters, order_by=order_by or "-created_on"
        )
        return Page.create(
            items=[ActivityLogResponse.model_validate(log) for log in page.items],
            total=page.total,
            params=params,
        )
