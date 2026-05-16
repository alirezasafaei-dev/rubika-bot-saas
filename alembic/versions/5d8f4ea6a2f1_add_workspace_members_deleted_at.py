"""add workspace_members deleted_at for soft delete compatibility

Revision ID: 5d8f4ea6a2f1
Revises: 4c8e2e7a6d1b
Create Date: 2026-05-17 00:00:00.000000+00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "5d8f4ea6a2f1"
down_revision = "4c8e2e7a6d1b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'workspace_members'
              AND column_name = 'deleted_at'
            LIMIT 1
            """
        )
    ).fetchone()

    if not result:
        op.add_column(
            "workspace_members",
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'workspace_members'
              AND column_name = 'deleted_at'
            LIMIT 1
            """
        )
    ).fetchone()

    if result:
        op.drop_column("workspace_members", "deleted_at")
