from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.model import ActivityLog


async def log_activity(
    session: AsyncSession,
    *,
    organization_id: UUID,
    event_type: str,
    description: str,
    user_id: UUID | None = None,
    clinic_id: UUID | None = None,
    patient_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
) -> ActivityLog:
    log = ActivityLog(
        organization_id=organization_id,
        clinic_id=clinic_id,
        patient_id=patient_id,
        user_id=user_id,
        event_type=event_type,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    session.add(log)
    await session.flush()
    await session.refresh(log)
    return log
