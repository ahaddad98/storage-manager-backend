import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import BaseModel
from core.models.tenant_mixin import ClinicMixin, CreatedByMixin, OrganizationMixin


class TreatmentPlan(BaseModel, OrganizationMixin, ClinicMixin, CreatedByMixin):
    __tablename__ = "treatment_plans"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dentist_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    estimated_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    items = relationship("TreatmentItem", back_populates="plan", lazy="selectin")


class TreatmentItem(BaseModel, OrganizationMixin):
    __tablename__ = "treatment_items"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("treatment_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tooth_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="planned", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan = relationship("TreatmentPlan", back_populates="items")
