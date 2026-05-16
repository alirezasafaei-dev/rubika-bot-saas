"""make workspace slug nullable for model compatibility

Revision ID: 4c8e2e7a6d1b
Revises: 3f4a8e2c9c1b
Create Date: 2026-05-16 00:00:00.000000+00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "4c8e2e7a6d1b"
down_revision = "3f4a8e2c9c1b"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    conn = op.get_bind()
    return (
        conn.execute(
            sa.text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = :table_name
                  AND column_name = :column_name
                LIMIT 1
                """
            ),
            {"table_name": table_name, "column_name": column_name},
        ).fetchone()
        is not None
    )


def upgrade() -> None:
    if _column_exists("workspaces", "slug"):
        op.alter_column("workspaces", "slug", existing_type=sa.String(120), nullable=True)


def downgrade() -> None:
    if _column_exists("workspaces", "slug"):
        # Keep data safe before re-applying strict non-null constraint.
        op.execute(
            """
            UPDATE workspaces
            SET slug = 'workspace-' || id::text
            WHERE slug IS NULL OR slug = ''
            """
        )
        op.alter_column("workspaces", "slug", existing_type=sa.String(120), nullable=False)
