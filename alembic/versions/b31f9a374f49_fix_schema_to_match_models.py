"""fix_schema_to_match_models

Revision ID: models
Revises: 201d39123257
Create Date: 2026-05-07 20:55:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'models'
down_revision = '201d39123257'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Fix users table - remove duplicate hashed_password column
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'hashed_password'
    """)).fetchone()

    conn.execute(sa.text("DROP INDEX IF EXISTS ix_workspaces_owner_id"))

    if result:
        op.drop_column('users', 'password_hash')
    else:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')

    # 2. Make full_name NOT NULL
    op.execute("UPDATE users SET full_name = phone WHERE full_name IS NULL OR full_name = ''")
    op.alter_column('users', 'full_name',
                    existing_type=sa.String(255),
                    nullable=False,
                    server_default='')

    # 3. Add is_active column
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # 4. Rename owner_id to created_by_user_id
    op.alter_column('workspaces', 'owner_id', new_column_name='created_by_user_id')
    op.create_index(op.f('ix_workspaces_owner_id'), 'workspaces', ['created_by_user_id'])

    # 5. Add slug and description
    op.add_column('workspaces', sa.Column('slug', sa.String(120), nullable=False, server_default=''))
    op.execute("""
        UPDATE workspaces
        SET slug = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g'))
        WHERE slug = ''
    """)
    op.alter_column('workspaces', 'slug', server_default=None)
    op.create_index(op.f('ix_workspaces_slug'), 'workspaces', ['slug'], unique=True)

    op.add_column('workspaces', sa.Column('description', sa.Text(), nullable=True))

    # 6. Update workspace_members table
    op.alter_column('workspace_members', 'created_at', new_column_name='joined_at')
    op.drop_column('workspace_members', 'updated_at')

    # 7. Add refresh_tokens table (idempotent if previous migration already created it)
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("refresh_tokens"):
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(64), nullable=False),
            sa.Column(
                "is_revoked",
                sa.Boolean(),
                server_default="false",
                nullable=False,
            ),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_refresh_tokens_token_hash"),
            "refresh_tokens",
            ["token_hash"],
            unique=True,
        )
        op.create_index(
            op.f("ix_refresh_tokens_user_id"),
            "refresh_tokens",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    # Drop refresh_tokens table
    op.drop_table('refresh_tokens')

    # Restore workspace_members
    op.add_column('workspace_members', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('workspace_members', 'joined_at', new_column_name='created_at')

    # Remove columns from workspaces
    op.drop_column('workspaces', 'description')
    op.drop_index(op.f('ix_workspaces_slug'), table_name='workspaces')
    op.drop_column('workspaces', 'slug')
    op.drop_index(op.f('ix_workspaces_owner_id'), table_name='workspaces')
    op.alter_column('workspaces', 'created_by_user_id', new_column_name='owner_id')
    op.create_index(op.f('ix_workspaces_owner_id'), 'workspaces', ['owner_id'])

    # Remove columns from users
    op.drop_column('users', 'is_active')
    op.alter_column('users', 'full_name',
                    existing_type=sa.String(255),
                    nullable=True,
                    server_default=None)
    # Check if password_hash exists
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'password_hash'
    """)).fetchone()
    if not result:
        op.alter_column('users', 'hashed_password', new_column_name='password_hash')
