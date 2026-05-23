"""add auto reply flow fields

Revision ID: a4d9e8b6c1f0
Revises: 9a2c7f4d1e22
Create Date: 2026-05-20 01:10:00.000000+00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "a4d9e8b6c1f0"
down_revision = "9a2c7f4d1e22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("auto_replies")}

    if "match_type" not in columns:
        match_type_enum = sa.Enum("contains", "exact", name="auto_reply_match_type")
        match_type_enum.create(op.get_bind(), checkfirst=True)
        op.add_column(
            "auto_replies",
            sa.Column(
                "match_type",
                match_type_enum,
                nullable=False,
                server_default="contains",
            ),
        )
        op.alter_column("auto_replies", "match_type", server_default=None)

    if "rich_reply_json" not in columns:
        op.add_column("auto_replies", sa.Column("rich_reply_json", sa.Text(), nullable=True))

    if "next_step_id" not in columns:
        op.add_column("auto_replies", sa.Column("next_step_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_auto_replies_next_step_id_auto_replies",
            "auto_replies",
            "auto_replies",
            ["next_step_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("auto_replies")}
    if "next_step_id" in columns:
        op.drop_constraint(
            "fk_auto_replies_next_step_id_auto_replies",
            "auto_replies",
            type_="foreignkey",
        )
        op.drop_column("auto_replies", "next_step_id")
    if "rich_reply_json" in columns:
        op.drop_column("auto_replies", "rich_reply_json")
    if "match_type" in columns:
        op.drop_column("auto_replies", "match_type")
    sa.Enum(name="auto_reply_match_type").drop(op.get_bind(), checkfirst=True)
