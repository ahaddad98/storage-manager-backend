from decimal import Decimal
from uuid import UUID

from app.billing.repository import InvoiceItemRepository, InvoiceRepository, PaymentRepository
from app.billing.schema import (
    InvoiceCreate,
    InvoiceFilter,
    InvoiceItemCreate,
    InvoiceItemFilter,
    InvoiceItemResponse,
    InvoiceItemUpdate,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentCreate,
    PaymentFilter,
    PaymentResponse,
    PaymentUpdate,
)
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext
from core.utils.pagination import Page, PaginationParams


class BillingService:
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        invoice_item_repository: InvoiceItemRepository,
        payment_repository: PaymentRepository,
        tenant: TenantContext,
    ):
        self.invoice_repository = invoice_repository
        self.invoice_item_repository = invoice_item_repository
        self.payment_repository = payment_repository
        self.tenant = tenant

    async def _recalculate_invoice(self, invoice_id: UUID) -> None:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            return
        items = await self.invoice_item_repository.list_raw(
            filters=InvoiceItemFilter(invoice_id=invoice_id),
            limit=1000,
        )
        subtotal = sum((item.total for item in items), Decimal("0"))
        total_amount = subtotal - invoice.discount
        await self.invoice_repository.update_from_dict(
            invoice,
            {"subtotal": subtotal, "total_amount": total_amount},
        )

    async def create_invoice(self, data: InvoiceCreate) -> InvoiceResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        invoice = await self.invoice_repository.create(data, created_by=self.tenant.user_id)
        return InvoiceResponse.model_validate(invoice)

    async def get_invoice(self, invoice_id: UUID) -> InvoiceResponse:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        return InvoiceResponse.model_validate(invoice)

    async def list_invoices(
        self,
        params: PaginationParams,
        filters: InvoiceFilter | None = None,
        order_by: str | None = None,
    ) -> Page[InvoiceResponse]:
        page = await self.invoice_repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[InvoiceResponse.model_validate(i) for i in page.items],
            total=page.total,
            params=params,
        )

    async def update_invoice(self, invoice_id: UUID, data: InvoiceUpdate) -> InvoiceResponse:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        updated = await self.invoice_repository.update(invoice, data)
        if data.discount is not None:
            await self._recalculate_invoice(invoice_id)
            updated = await self.invoice_repository.get_by_id(invoice_id)
        return InvoiceResponse.model_validate(updated)

    async def delete_invoice(self, invoice_id: UUID, hard: bool = False) -> None:
        deleted = await self.invoice_repository.delete(invoice_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Invoice {invoice_id} not found")

    async def restore_invoice(self, invoice_id: UUID) -> InvoiceResponse:
        invoice = await self.invoice_repository.restore(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found or not deleted")
        return InvoiceResponse.model_validate(invoice)

    async def create_invoice_item(
        self, invoice_id: UUID, data: InvoiceItemCreate
    ) -> InvoiceItemResponse:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        item_data = data.model_copy()
        if item_data.total == Decimal("0"):
            item_data.total = item_data.unit_price * item_data.quantity
        item = await self.invoice_item_repository.create(item_data, invoice_id=invoice_id)
        await self._recalculate_invoice(invoice_id)
        return InvoiceItemResponse.model_validate(item)

    async def list_invoice_items(
        self,
        invoice_id: UUID,
        params: PaginationParams,
        filters: InvoiceItemFilter | None = None,
        order_by: str | None = None,
    ) -> Page[InvoiceItemResponse]:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        item_filters = filters or InvoiceItemFilter()
        item_filters.invoice_id = invoice_id
        page = await self.invoice_item_repository.list(
            params=params, filters=item_filters, order_by=order_by
        )
        return Page.create(
            items=[InvoiceItemResponse.model_validate(i) for i in page.items],
            total=page.total,
            params=params,
        )

    async def get_invoice_item(self, invoice_id: UUID, item_id: UUID) -> InvoiceItemResponse:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        item = await self.invoice_item_repository.get_by_id_for_invoice(item_id, invoice_id)
        if item is None:
            raise NotFoundException(f"Invoice item {item_id} not found in invoice {invoice_id}")
        return InvoiceItemResponse.model_validate(item)

    async def update_invoice_item(
        self, invoice_id: UUID, item_id: UUID, data: InvoiceItemUpdate
    ) -> InvoiceItemResponse:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        item = await self.invoice_item_repository.get_by_id_for_invoice(item_id, invoice_id)
        if item is None:
            raise NotFoundException(f"Invoice item {item_id} not found in invoice {invoice_id}")
        updated = await self.invoice_item_repository.update(item, data)
        if data.quantity is not None or data.unit_price is not None:
            qty = updated.quantity
            price = updated.unit_price
            await self.invoice_item_repository.update_from_dict(updated, {"total": qty * price})
        await self._recalculate_invoice(invoice_id)
        refreshed = await self.invoice_item_repository.get_by_id_for_invoice(item_id, invoice_id)
        return InvoiceItemResponse.model_validate(refreshed)

    async def delete_invoice_item(
        self, invoice_id: UUID, item_id: UUID, hard: bool = False
    ) -> None:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        item = await self.invoice_item_repository.get_by_id_for_invoice(item_id, invoice_id)
        if item is None:
            raise NotFoundException(f"Invoice item {item_id} not found in invoice {invoice_id}")
        await self.invoice_item_repository.delete(item_id, hard=hard)
        await self._recalculate_invoice(invoice_id)

    async def create_payment(self, data: PaymentCreate) -> PaymentResponse:
        self.tenant.require_clinic_access(data.clinic_id)
        if data.invoice_id:
            invoice = await self.invoice_repository.get_by_id(data.invoice_id)
            if invoice is None or invoice.clinic_id != data.clinic_id:
                raise NotFoundException(f"Invoice {data.invoice_id} not found")
        payment = await self.payment_repository.create(
            data,
            received_by=data.received_by or self.tenant.user_id,
        )
        if payment.invoice_id:
            invoice = await self.invoice_repository.get_by_id(payment.invoice_id)
            if invoice:
                new_paid = invoice.amount_paid + payment.amount
                status = "paid" if new_paid >= invoice.total_amount else "partial"
                await self.invoice_repository.update_from_dict(
                    invoice,
                    {"amount_paid": new_paid, "status": status},
                )
        return PaymentResponse.model_validate(payment)

    async def get_payment(self, payment_id: UUID) -> PaymentResponse:
        payment = await self.payment_repository.get_by_id(payment_id)
        if payment is None:
            raise NotFoundException(f"Payment {payment_id} not found")
        return PaymentResponse.model_validate(payment)

    async def list_payments(
        self,
        params: PaginationParams,
        filters: PaymentFilter | None = None,
        order_by: str | None = None,
    ) -> Page[PaymentResponse]:
        page = await self.payment_repository.list(params=params, filters=filters, order_by=order_by)
        return Page.create(
            items=[PaymentResponse.model_validate(p) for p in page.items],
            total=page.total,
            params=params,
        )

    async def update_payment(self, payment_id: UUID, data: PaymentUpdate) -> PaymentResponse:
        payment = await self.payment_repository.get_by_id(payment_id)
        if payment is None:
            raise NotFoundException(f"Payment {payment_id} not found")
        updated = await self.payment_repository.update(payment, data)
        return PaymentResponse.model_validate(updated)

    async def delete_payment(self, payment_id: UUID, hard: bool = False) -> None:
        deleted = await self.payment_repository.delete(payment_id, hard=hard)
        if not deleted:
            raise NotFoundException(f"Payment {payment_id} not found")
