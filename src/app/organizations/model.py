from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import BaseModel


class Organization(BaseModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="dental_clinic",
        server_default="dental_clinic",
    )
    enabled_modules: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    billing_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    clinics = relationship("Clinic", back_populates="organization", lazy="selectin")
    memberships = relationship("Membership", back_populates="organization", lazy="selectin")
