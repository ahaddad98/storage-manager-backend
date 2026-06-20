import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import BaseModel
from core.models.tenant_mixin import OrganizationMixin


class Membership(BaseModel, OrganizationMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_user_org"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="assistant")
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invitation_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")
    clinic_assignments = relationship(
        "ClinicAssignment", back_populates="membership", lazy="selectin"
    )


class ClinicAssignment(BaseModel, OrganizationMixin):
    __tablename__ = "clinic_assignments"
    __table_args__ = (UniqueConstraint("membership_id", "clinic_id", name="uq_membership_clinic"),)

    membership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memberships.id", ondelete="CASCADE"),
        nullable=False,
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    membership = relationship("Membership", back_populates="clinic_assignments")
