import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import BaseModel
from core.models.tenant_mixin import ClinicMixin, OrganizationMixin


class DentalChart(BaseModel, OrganizationMixin, ClinicMixin):
    __tablename__ = "dental_charts"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    teeth = relationship("ToothRecord", back_populates="chart", lazy="selectin")


class ToothRecord(BaseModel, OrganizationMixin):
    __tablename__ = "tooth_records"
    __table_args__ = ({"comment": "Individual tooth records in dental chart"},)

    chart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dental_charts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tooth_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="healthy", nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    planned_treatments: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_treatments: Mapped[str | None] = mapped_column(Text, nullable=True)

    chart = relationship("DentalChart", back_populates="teeth")
