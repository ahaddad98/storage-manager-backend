from app.organizations.repository import OrganizationRepository
from app.organizations.schema import OrganizationResponse, OrganizationUpdate
from core.business_modules import normalize_business_type, resolve_enabled_modules
from core.exceptions import NotFoundException


class OrganizationService:
    def __init__(self, repository: OrganizationRepository):
        self.repository = repository

    async def get_current(self) -> OrganizationResponse:
        org = await self.repository.get_current()
        if org is None:
            raise NotFoundException("Organization not found")
        return OrganizationResponse.model_validate(org)

    async def update(self, data: OrganizationUpdate) -> OrganizationResponse:
        org = await self.repository.get_current()
        if org is None:
            raise NotFoundException("Organization not found")
        update_data = data.model_copy()
        target_business_type = normalize_business_type(
            data.business_type if data.business_type is not None else org.business_type
        )
        if data.business_type is not None:
            update_data.business_type = target_business_type
        if data.enabled_modules is not None:
            update_data.enabled_modules = resolve_enabled_modules(
                target_business_type,
                data.enabled_modules,
            )
        elif data.business_type is not None:
            update_data.enabled_modules = None
        updated = await self.repository.update(org, update_data)
        return OrganizationResponse.model_validate(updated)
