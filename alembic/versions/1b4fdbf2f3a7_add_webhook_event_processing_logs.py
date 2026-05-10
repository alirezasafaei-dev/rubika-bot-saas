"""add webhook event processing logs

Revision ID: 1b4fdbf2f3a7
Revises: eac588709f37
Create Date: 2026-05-10 14:25:28.000000+00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "1b4fdbf2f3a7"
down_revision = "eac588709f37"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "channel_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("message_id", sa.String(length=128), nullable=True),
        sa.Column("sender_rubika_user_id", sa.String(length=64), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_webhook_events_channel_id"), "webhook_events", ["channel_id"], unique=False
    )
    op.create_index(
        op.f("ix_webhook_events_event_type"), "webhook_events", ["event_type"], unique=False
    )
    op.create_index(
        op.f("ix_webhook_events_message_id"), "webhook_events", ["message_id"], unique=False
    )
    op.create_index(
        op.f("uq_webhook_events_dedupe"),
        "webhook_events",
        ["channel_id", "event_type", "message_id"],
        unique=True,
        sqlite_where=sa.text("message_id IS NOT NULL"),
    )

    op.create_table(
        "message_processing_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("filter_rule_id", sa.Integer(), nullable=True),
        sa.Column("auto_reply_rule_id", sa.Integer(), nullable=True),
        sa.Column(
            "outcome",
            sa.Enum(
                "duplicate",
                "filter_blocked",
                "auto_replied",
                "no_match",
                "delivery_result",
                "error",
                name="processing_outcome",
            ),
            nullable=False,
        ),
        sa.Column("message_excerpt", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["webhook_events.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["filter_rule_id"], ["filters.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            "auto_reply_rule_id",
            ["auto_replies.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_message_processing_logs_event_id"),
        "message_processing_logs",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_processing_logs_channel_id"),
        "message_processing_logs",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_processing_logs_filter_rule_id"),
        "message_processing_logs",
        ["filter_rule_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_processing_logs_auto_reply_rule_id"),
        "message_processing_logs",
        ["auto_reply_rule_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_processing_logs_outcome"),
        "message_processing_logs",
        ["outcome"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("message_processing_logs")
    op.drop_index(op.f("ix_webhook_events_message_id"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_event_type"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_channel_id"), table_name="webhook_events")
    op.drop_index(op.f("uq_webhook_events_dedupe"), table_name="webhook_events")
    op.drop_table("webhook_events")
