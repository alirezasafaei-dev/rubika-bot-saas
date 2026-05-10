"""merge scheduled posts migration heads

Revision ID: eac588709f37
Revises: 2903b9c7c51c, 7815ab12f360
Create Date: 2026-05-10 00:10:00.000000+00:00
"""
from __future__ import annotations

revision = "eac588709f37"
down_revision = ("2903b9c7c51c", "7815ab12f360")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge migration branch head for scheduled posts workflow.
    return None


def downgrade() -> None:
    # Merge point can be reverted by dropping both branches explicitly.
    return None
