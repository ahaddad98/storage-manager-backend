from __future__ import annotations

from collections.abc import Iterable


class BusinessType:
    DENTAL_CLINIC = "dental_clinic"
    PHONE_STORE = "phone_store"
    DROGUERIE = "droguerie"
    RETAIL = "retail"


class ModuleKey:
    DASHBOARD = "dashboard"
    PATIENTS = "patients"
    APPOINTMENTS = "appointments"
    DENTAL_CHART = "dental_chart"
    TREATMENTS = "treatments"
    BILLING = "billing"
    INVENTORY = "inventory"
    REPORTS = "reports"
    STAFF = "staff"
    CLINICS = "clinics"
    SETTINGS = "settings"
    DOCUMENTS = "documents"
    NOTIFICATIONS = "notifications"
    CATALOG = "catalog"


SUPPORTED_BUSINESS_TYPES = {
    BusinessType.DENTAL_CLINIC,
    BusinessType.PHONE_STORE,
    BusinessType.DROGUERIE,
    BusinessType.RETAIL,
}

SUPPORTED_MODULES = {
    ModuleKey.DASHBOARD,
    ModuleKey.PATIENTS,
    ModuleKey.APPOINTMENTS,
    ModuleKey.DENTAL_CHART,
    ModuleKey.TREATMENTS,
    ModuleKey.BILLING,
    ModuleKey.INVENTORY,
    ModuleKey.CATALOG,
    ModuleKey.REPORTS,
    ModuleKey.STAFF,
    ModuleKey.CLINICS,
    ModuleKey.SETTINGS,
    ModuleKey.DOCUMENTS,
    ModuleKey.NOTIFICATIONS,
    ModuleKey.CATALOG,
}

DENTAL_DEFAULT_MODULES = [
    ModuleKey.DASHBOARD,
    ModuleKey.PATIENTS,
    ModuleKey.APPOINTMENTS,
    ModuleKey.DENTAL_CHART,
    ModuleKey.TREATMENTS,
    ModuleKey.BILLING,
    ModuleKey.INVENTORY,
    ModuleKey.REPORTS,
    ModuleKey.STAFF,
    ModuleKey.CLINICS,
    ModuleKey.SETTINGS,
    ModuleKey.DOCUMENTS,
    ModuleKey.NOTIFICATIONS,
    ModuleKey.CATALOG,
]

SHARED_DEFAULT_MODULES = [
    ModuleKey.DASHBOARD,
    ModuleKey.BILLING,
    ModuleKey.INVENTORY,
    ModuleKey.REPORTS,
    ModuleKey.STAFF,
    ModuleKey.CLINICS,
    ModuleKey.SETTINGS,
    ModuleKey.DOCUMENTS,
    ModuleKey.NOTIFICATIONS,
]

BUSINESS_TYPE_DEFAULT_MODULES = {
    BusinessType.DENTAL_CLINIC: DENTAL_DEFAULT_MODULES,
    BusinessType.PHONE_STORE: SHARED_DEFAULT_MODULES,
    BusinessType.DROGUERIE: SHARED_DEFAULT_MODULES,
    BusinessType.RETAIL: SHARED_DEFAULT_MODULES,
}

DENTAL_ONLY_MODULES = {
    ModuleKey.PATIENTS,
    ModuleKey.APPOINTMENTS,
    ModuleKey.DENTAL_CHART,
    ModuleKey.TREATMENTS,
}


def normalize_business_type(value: str | None) -> str:
    if value in SUPPORTED_BUSINESS_TYPES:
        return value
    return BusinessType.DENTAL_CLINIC


def default_modules_for_business_type(business_type: str | None) -> list[str]:
    normalized = normalize_business_type(business_type)
    return list(BUSINESS_TYPE_DEFAULT_MODULES[normalized])


def resolve_enabled_modules(
    business_type: str | None,
    enabled_modules: Iterable[str] | None,
) -> list[str]:
    if enabled_modules is None:
        return default_modules_for_business_type(business_type)

    allowed_for_business = set(default_modules_for_business_type(business_type))
    resolved: list[str] = []
    for module in enabled_modules:
        if (
            module in SUPPORTED_MODULES
            and module in allowed_for_business
            and module not in resolved
        ):
            resolved.append(module)
    return resolved
