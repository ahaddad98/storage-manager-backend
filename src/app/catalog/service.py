from datetime import datetime, timezone
from uuid import UUID

from app.catalog.presets import (
    get_catalog_metadata,
    get_inventory_starter_items,
    get_treatment_templates,
)
from app.catalog.schema import (
    AppliedInventoryItem,
    ApplyInventoryStarterKitResponse,
    CatalogInventoryItem,
    CatalogTreatmentTemplate,
    PresetCatalogResponse,
)
from app.clinics.repository import ClinicRepository
from app.inventory.repository import InventoryItemRepository
from app.inventory.schema import InventoryItemCreate, InventoryItemFilter
from core.exceptions import NotFoundException
from core.middleware.auth.tenant import TenantContext


class PresetCatalogService:
    def __init__(
        self,
        clinic_repository: ClinicRepository,
        item_repository: InventoryItemRepository,
        tenant: TenantContext,
    ):
        self.clinic_repository = clinic_repository
        self.item_repository = item_repository
        self.tenant = tenant

    def get_catalog(self) -> PresetCatalogResponse:
        metadata = get_catalog_metadata(self.tenant.business_type)
        return PresetCatalogResponse(
            business_type=self.tenant.business_type,
            title=metadata["title"],
            description=metadata["description"],
            inventory_items=[
                CatalogInventoryItem(**item)
                for item in get_inventory_starter_items(self.tenant.business_type)
            ],
            treatment_templates=[
                CatalogTreatmentTemplate(**template)
                for template in get_treatment_templates(self.tenant.business_type)
            ],
        )

    async def apply_inventory_starter_kit(
        self, clinic_id: UUID
    ) -> ApplyInventoryStarterKitResponse:
        self.tenant.require_clinic_access(clinic_id)
        clinic = await self.clinic_repository.get_by_id(clinic_id)
        if clinic is None:
            raise NotFoundException(f"Clinic {clinic_id} not found")

        results: list[AppliedInventoryItem] = []
        created_count = 0
        skipped_count = 0

        for preset in get_inventory_starter_items(self.tenant.business_type):
            existing = await self.item_repository.get_first(
                InventoryItemFilter(clinic_id=clinic_id, sku=preset["sku"])
            )
            if existing:
                skipped_count += 1
                results.append(
                    AppliedInventoryItem(
                        sku=preset["sku"],
                        name=preset["name"],
                        status="skipped",
                        item_id=existing.id,
                    )
                )
                continue

            item = await self.item_repository.create(
                InventoryItemCreate(
                    clinic_id=clinic_id,
                    name=preset["name"],
                    sku=preset["sku"],
                    category=preset["category"],
                    quantity=0,
                    unit=preset["unit"],
                    min_stock_level=preset["min_stock_level"],
                    notes=preset.get("notes"),
                )
            )
            created_count += 1
            results.append(
                AppliedInventoryItem(
                    sku=preset["sku"],
                    name=preset["name"],
                    status="created",
                    item_id=item.id,
                )
            )

        return ApplyInventoryStarterKitResponse(
            clinic_id=clinic_id,
            created_count=created_count,
            skipped_count=skipped_count,
            items=results,
            applied_on=datetime.now(timezone.utc),
        )
