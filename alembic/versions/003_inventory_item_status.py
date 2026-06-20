"""Add inventory item condition status.

Revision ID: 003_inventory_status
Revises: 002_dental_saas
Create Date: 2026-06-20
"""

from typing import Union

import sqlalchemy as sa
from alembic import op


revision: str = "003_inventory_status"
down_revision: Union[str, None] = "002_dental_saas"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column(
        "inventory_items",
        sa.Column("status", sa.String(length=20), server_default="ok", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("inventory_items", "status")
