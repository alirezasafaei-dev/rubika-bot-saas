"""add filters.reason column if missing

Revision ID: 8c1f9d2a4b77
Revises: 5d8f4ea6a2f1
Create Date: 2026-05-20 00:00:00.000000+00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "8c1f9d2a4b77"
down_revision = "5d8f4ea6a2f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("filters")}
    if "reason" not in columns:
        op.add_column("filters", sa.Column("reason", sa.String(length=500), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("filters")}
    if "reason" in columns:
        op.drop_column("filters", "reason")
