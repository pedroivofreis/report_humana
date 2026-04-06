"""update_user_status_enum

Revision ID: a1b2c3d4e5f6
Revises: 6659acb001e9
Create Date: 2026-02-27 14:03:06.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '6659acb001e9'
branch_labels = None
depends_on = None

NEW_VALUES = ('REGISTERED', 'ACTIVE', 'INACTIVE', 'WITH_PENDENCY', 'RESCISSION')
OLD_VALUES = ('REGISTERED', 'APPROVED', 'PENDING', 'REJECTED')


def upgrade():
    op.execute("UPDATE users SET status = 'ACTIVE'      WHERE status = 'APPROVED'")
    op.execute("UPDATE users SET status = 'REGISTERED'  WHERE status = 'PENDING'")
    op.execute("UPDATE users SET status = 'INACTIVE'    WHERE status = 'REJECTED'")
    op.alter_column(
        'users',
        'status',
        existing_type=sa.Enum(*OLD_VALUES, name='user_status', native_enum=False),
        type_=sa.Enum(*NEW_VALUES, name='user_status', native_enum=False),
        existing_nullable=False,
        existing_server_default='REGISTERED',
    )


def downgrade():
    op.execute("UPDATE users SET status = 'APPROVED' WHERE status = 'ACTIVE'")
    op.execute("UPDATE users SET status = 'REJECTED' WHERE status = 'INACTIVE'")
    op.execute("UPDATE users SET status = 'PENDING'  WHERE status = 'WITH_PENDENCY'")
    op.execute("UPDATE users SET status = 'REJECTED' WHERE status = 'RESCISSION'")

    op.alter_column(
        'users',
        'status',
        existing_type=sa.Enum(*NEW_VALUES, name='user_status', native_enum=False),
        type_=sa.Enum(*OLD_VALUES, name='user_status', native_enum=False),
        existing_nullable=False,
        existing_server_default='REGISTERED',
    )
