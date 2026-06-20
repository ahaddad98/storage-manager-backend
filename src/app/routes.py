from fastapi import APIRouter

from app.appointments.router import router as appointments_router
from app.auth.router import router as auth_router
from app.billing.router import router as billing_router
from app.catalog.router import router as catalog_router
from app.clinics.router import router as clinics_router
from app.dental_chart.router import router as dental_chart_router
from app.documents.router import router as documents_router
from app.inventory.router import router as inventory_router
from app.items.router import router as items_router
from app.notifications.router import router as notifications_router
from app.organizations.router import router as organizations_router
from app.patients.router import router as patients_router
from app.reports.router import router as reports_router
from app.staff.router import router as staff_router
from app.treatment_plans.router import router as treatment_plans_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(items_router, prefix="/items", tags=["items"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
api_router.include_router(clinics_router, prefix="/clinics", tags=["clinics"])
api_router.include_router(patients_router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(dental_chart_router, prefix="/dental-chart", tags=["dental-chart"])
api_router.include_router(
    treatment_plans_router, prefix="/treatment-plans", tags=["treatment-plans"]
)
api_router.include_router(billing_router, prefix="/billing", tags=["billing"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(staff_router, prefix="/staff", tags=["staff"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
