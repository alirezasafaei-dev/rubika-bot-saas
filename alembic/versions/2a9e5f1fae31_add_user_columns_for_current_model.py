"""add missing user columns for current model

Revision ID: 2a9e5f1fae31
Revises: 1b4fdbf2f3a7
Create Date: 2026-05-16
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a9e5f1fae31"
down_revision: str | None = "1b4fdbf2f3a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(
    inspector: Any, table: str, column: str
) -> bool:
    return column in {row["name"] for row in inspector.get_columns(table)}


def _has_type(type_name: str) -> bool:
    connection = op.get_bind()
    result = connection.execute(
        sa.text(
            """
            SELECT 1
            FROM pg_type t
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname = :type_name
              AND n.nspname = 'public'
            LIMIT 1
            """
        ),
        {"type_name": type_name},
    ).fetchone()
    return result is not None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if not _has_column(inspector, "users", "username"):
        op.add_column(
            "users",
            sa.Column("username", sa.String(100), nullable=True),
        )
        op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)")

    if not _has_column(inspector, "users", "role"):
        if not _has_type("user_role"):
            op.execute(
                """
                CREATE TYPE user_role AS ENUM ('owner', 'admin', 'member')
                """
            )
        op.add_column(
            "users",
            sa.Column(
                "role",
                sa.Enum("owner", "admin", "member", name="user_role"),
                nullable=False,
                server_default="member",
            ),
        )

    if not _has_column(inspector, "users", "status"):
        if not _has_type("user_status"):
            op.execute(
                """
                CREATE TYPE user_status AS ENUM ('active', 'blocked', 'deleted')
                """
            )
        op.add_column(
            "users",
            sa.Column(
                "status",
                sa.Enum("active", "blocked", "deleted", name="user_status"),
                nullable=False,
                server_default="active",
            ),
        )

    if not _has_column(inspector, "users", "deleted_at"):
        op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    if _has_column(sa.inspect(op.get_bind()), "users", "deleted_at"):
        op.drop_column("users", "deleted_at")

    if _has_column(sa.inspect(op.get_bind()), "users", "status"):
        op.drop_column("users", "status")

    if _has_column(sa.inspect(op.get_bind()), "users", "role"):
        op.drop_column("users", "role")

    if _has_column(sa.inspect(op.get_bind()), "users", "username"):
        op.execute("DROP INDEX IF EXISTS ix_users_username")
        op.drop_column("users", "username")

    op.execute("DROP TYPE IF EXISTS user_status")
    op.execute("DROP TYPE IF EXISTS user_role")
