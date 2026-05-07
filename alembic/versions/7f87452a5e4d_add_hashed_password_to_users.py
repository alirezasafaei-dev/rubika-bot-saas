# alembic/versions/7f87452a5e4d_add_hashed_password_to_users.py
"""add hashed_password to users

Revision ID: 7f87452a5e4d
Revises: cbb716c6ed46
Create Date: 2026-05-07 12:54:19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f87452a5e4d"
down_revision: str | None = "cbb716c6ed46"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "hashed_password", sa.String(length=255), nullable=False, server_default=""
        ),
    )
    op.alter_column("users", "hashed_password", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
