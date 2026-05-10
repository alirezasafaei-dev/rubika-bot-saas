"""add queued status for scheduled posts

Revision ID: 2903b9c7c51c
Revises: models
Create Date: 2026-05-10 00:00:00.000000+00:00
"""
from __future__ import annotations

from alembic import op

revision = "2903b9c7c51c"
down_revision = "models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE post_status ADD VALUE IF NOT EXISTS 'queued'")

    # SQLite and other local test backends do not enforce enum constraints.


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without full type recreation;
    # keep this migration one-way unless a full migration is introduced.
    if op.get_bind().dialect.name != "postgresql":
        return
