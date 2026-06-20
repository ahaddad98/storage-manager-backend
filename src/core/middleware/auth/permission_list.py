from core.exceptions import ForbiddenException, UnauthorizedException

__all__ = ["UnauthorizedException", "ForbiddenException", "Permission", "Role", "ROLE_PERMISSIONS"]


class Permission:
    # Legacy items
    ITEMS_READ = "items:read"
    ITEMS_WRITE = "items:write"
    ITEMS_DELETE = "items:delete"

    # Patients
    PATIENTS_READ = "patients.read"
    PATIENTS_CREATE = "patients.create"
    PATIENTS_UPDATE = "patients.update"
    PATIENTS_DELETE = "patients.delete"

    # Appointments
    APPOINTMENTS_READ = "appointments.read"
    APPOINTMENTS_MANAGE = "appointments.manage"

    # Dental chart
    DENTAL_CHART_READ = "dental_chart.read"
    DENTAL_CHART_MANAGE = "dental_chart.manage"

    # Treatment plans
    TREATMENTS_READ = "treatments.read"
    TREATMENTS_MANAGE = "treatments.manage"

    # Billing
    BILLING_READ = "billing.read"
    BILLING_MANAGE = "billing.manage"

    # Inventory
    INVENTORY_READ = "inventory.read"
    INVENTORY_MANAGE = "inventory.manage"

    # Reports
    REPORTS_VIEW = "reports.view"

    # Settings & staff
    SETTINGS_MANAGE = "settings.manage"
    STAFF_MANAGE = "staff.manage"
    CLINICS_MANAGE = "clinics.manage"

    # Documents
    DOCUMENTS_READ = "documents.read"
    DOCUMENTS_MANAGE = "documents.manage"

    # Notifications
    NOTIFICATIONS_READ = "notifications.read"
    NOTIFICATIONS_MANAGE = "notifications.manage"


class Role:
    OWNER = "owner"
    ADMIN = "admin"
    DENTIST = "dentist"
    ASSISTANT = "assistant"
    RECEPTIONIST = "receptionist"
    # Legacy
    USER = "user"
    VIEWER = "viewer"
