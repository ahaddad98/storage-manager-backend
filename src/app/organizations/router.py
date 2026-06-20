from typing import Annotated

from fastapi import APIRouter, Depends

from app.organizations.repository import OrganizationRepository
from app.organizations.schema import OrganizationResponse, OrganizationUpdate
from app.organizations.service import OrganizationService
from core.middleware.auth.exceptions import require_permission
from core.middleware.auth.permission_list import Permission

router = APIRouter()


def get_organization_service(
    repository: Annotated[OrganizationRepository, Depends()],
) -> OrganizationService:
    return OrganizationService(repository)


@router.get("", response_model=OrganizationResponse)
async def get_organization(
    _user: Annotated[dict, Depends(require_permission(Permission.SETTINGS_MANAGE))],
    service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationResponse:
    return await service.get_current()


@router.patch("", response_model=OrganizationResponse)
async def update_organization(
    data: OrganizationUpdate,
    _user: Annotated[dict, Depends(require_permission(Permission.SETTINGS_MANAGE))],
    service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationResponse:
    return await service.update(data)
