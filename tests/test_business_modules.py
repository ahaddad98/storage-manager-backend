from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from core.business_modules import (
    BusinessType,
    ModuleKey,
    default_modules_for_business_type,
    resolve_enabled_modules,
)
from core.middleware.auth.tenant import TenantContext


def test_dental_clinic_defaults_keep_existing_dental_modules() -> None:
    modules = default_modules_for_business_type(BusinessType.DENTAL_CLINIC)

    assert ModuleKey.PATIENTS in modules
    assert ModuleKey.APPOINTMENTS in modules
    assert ModuleKey.DENTAL_CHART in modules
    assert ModuleKey.TREATMENTS in modules
    assert ModuleKey.BILLING in modules
    assert ModuleKey.INVENTORY in modules


@pytest.mark.parametrize(
    "business_type",
    [BusinessType.PHONE_STORE, BusinessType.DROGUERIE, BusinessType.RETAIL],
)
def test_non_dental_defaults_hide_dental_workflows(business_type: str) -> None:
    modules = default_modules_for_business_type(business_type)

    assert ModuleKey.DENTAL_CHART not in modules
    assert ModuleKey.TREATMENTS not in modules
    assert ModuleKey.PATIENTS not in modules
    assert ModuleKey.APPOINTMENTS not in modules
    assert ModuleKey.INVENTORY in modules
    assert ModuleKey.BILLING in modules


def test_module_overrides_cannot_enable_unsupported_business_modules() -> None:
    modules = resolve_enabled_modules(
        BusinessType.PHONE_STORE,
        [ModuleKey.INVENTORY, ModuleKey.DENTAL_CHART, "unknown"],
    )

    assert modules == [ModuleKey.INVENTORY]


def test_tenant_context_denies_inaccessible_clinic() -> None:
    allowed_clinic_id = uuid4()
    tenant = TenantContext(
        user_id=uuid4(),
        organization_id=uuid4(),
        role="assistant",
        clinic_ids={allowed_clinic_id},
    )

    tenant.require_clinic_access(allowed_clinic_id)
    with pytest.raises(HTTPException) as exc:
        tenant.require_clinic_access(uuid4())

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
