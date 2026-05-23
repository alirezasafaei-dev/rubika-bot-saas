"""add filter match type and extend actions

Revision ID: 9a2c7f4d1e22
Revises: 8c1f9d2a4b77
Create Date: 2026-05-20 00:30:00.000000+00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "9a2c7f4d1e22"
down_revision = "8c1f9d2a4b77"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("filters")}
    if "match_type" not in columns:
        match_type_enum = sa.Enum(
            "contains",
            "regex",
            name="filter_match_type",
        )
        match_type_enum.create(op.get_bind(), checkfirst=True)
        op.add_column(
            "filters",
            sa.Column(
                "match_type",
                match_type_enum,
                nullable=False,
                server_default="contains",
            ),
        )
        op.alter_column("filters", "match_type", server_default=None)

    action_enum = sa.Enum(
        "delete",
        "warn",
        "ban",
        "flag",
        "shadow_block",
        name="filter_action",
    )
    action_enum.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("filters")}
    if "match_type" in columns:
        op.drop_column("filters", "match_type")
    sa.Enum(name="filter_match_type").drop(op.get_bind(), checkfirst=True)
