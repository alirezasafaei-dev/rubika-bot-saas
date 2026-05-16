"""restore workspaces owner_id compatibility column

Revision ID: 3f4a8e2c9c1b
Revises: 2a9e5f1fae31
Create Date: 2026-05-17
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "3f4a8e2c9c1b"
down_revision = "2a9e5f1fae31"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    connection = op.get_bind()
    result = connection.execute(
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
    return result is not None


def _rename_owner_column() -> None:
    if (
        _column_exists("workspaces", "created_by_user_id")
        and not _column_exists("workspaces", "owner_id")
    ):
        op.execute(
            sa.text(
                """
                ALTER TABLE workspaces
                RENAME COLUMN created_by_user_id TO owner_id
                """
            )
        )


def upgrade() -> None:
    _rename_owner_column()


def downgrade() -> None:
    if _column_exists("workspaces", "owner_id") and not _column_exists(
        "workspaces", "created_by_user_id"
    ):
        op.execute(
            sa.text(
                """
                ALTER TABLE workspaces
                RENAME COLUMN owner_id TO created_by_user_id
                """
            )
        )
