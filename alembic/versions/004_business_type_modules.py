"""Add organization business type and module visibility.

Revision ID: 004_business_type_modules
Revises: 003_inventory_status
Create Date: 2026-06-20
"""

from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "004_business_type_modules"
down_revision: Union[str, None] = "003_inventory_status"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "business_type",
            sa.String(length=50),
            server_default="dental_clinic",
            nullable=False,
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("enabled_modules", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "enabled_modules")
    op.drop_column("organizations", "business_type")
