import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import BaseModel
from core.models.tenant_mixin import ClinicMixin, CreatedByMixin, OrganizationMixin


class Patient(BaseModel, OrganizationMixin, ClinicMixin, CreatedByMixin):
    __tablename__ = "patients"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    medical_history = relationship(
        "MedicalHistory", back_populates="patient", uselist=False, lazy="selectin"
    )


class MedicalHistory(BaseModel, OrganizationMixin):
    __tablename__ = "medical_histories"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    chronic_diseases: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    pregnancy_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    smoking_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    previous_surgeries: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_alerts: Mapped[str | None] = mapped_column(Text, nullable=True)
    blood_pressure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    doctor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient = relationship("Patient", back_populates="medical_history")
