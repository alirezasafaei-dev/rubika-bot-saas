"""add scheduled posts table

Revision ID: 7815ab12f360
Revises: models
Create Date: 2026-05-08 11:40:48.379686+00:00

"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "7815ab12f360"
down_revision = "models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    if not inspector.has_table("channels"):
        return

    post_status = postgresql.ENUM(
        "pending",
        "queued",
        "sent",
        "failed",
        "cancelled",
        name="post_status_enum",
    )
    post_status.create(bind, checkfirst=True)

    if inspector.has_table("scheduled_posts"):
        return

    op.create_table(
        "scheduled_posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("scheduled_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(name="post_status_enum", native_enum=True, create_type=False),
            server_default=sa.text("'pending'::post_status_enum"),
            nullable=False,
        ),
        sa.Column("sent_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scheduled_posts_channel_id", "scheduled_posts", ["channel_id"])
    op.create_index("ix_scheduled_posts_scheduled_at", "scheduled_posts", ["scheduled_at"])
    op.create_index("ix_scheduled_posts_status", "scheduled_posts", ["status"])


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    if sa.inspect(bind).has_table("scheduled_posts"):
        op.drop_index("ix_scheduled_posts_status", table_name="scheduled_posts")
        op.drop_index("ix_scheduled_posts_scheduled_at", table_name="scheduled_posts")
        op.drop_index("ix_scheduled_posts_channel_id", table_name="scheduled_posts")
        op.drop_table("scheduled_posts")
