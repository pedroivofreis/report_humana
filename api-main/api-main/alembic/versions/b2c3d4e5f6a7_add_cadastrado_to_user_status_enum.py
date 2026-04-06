"""add_cadastrado_to_user_status_enum

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-27 17:59:44.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

OLD_VALUES = ('REGISTERED', 'ACTIVE', 'INACTIVE', 'WITH_PENDENCY', 'RESCISSION')
NEW_VALUES = ('REGISTERED', 'ACTIVE', 'INACTIVE', 'WITH_PENDENCY', 'RESCISSION', 'ENROLLED')


def upgrade():
    op.alter_column(
        'users',
        'status',
        existing_type=sa.Enum(*OLD_VALUES, name='user_status', native_enum=False),
        type_=sa.Enum(*NEW_VALUES, name='user_status', native_enum=False),
        existing_nullable=False,
        existing_server_default='REGISTERED',
    )


def downgrade():
    # Reassign any ENROLLED rows before removing the value
    op.execute("UPDATE users SET status = 'REGISTERED' WHERE status = 'ENROLLED'")

    op.alter_column(
        'users',
        'status',
        existing_type=sa.Enum(*NEW_VALUES, name='user_status', native_enum=False),
        type_=sa.Enum(*OLD_VALUES, name='user_status', native_enum=False),
        existing_nullable=False,
        existing_server_default='REGISTERED',
    )
