"""add_user_observations_table

Revision ID: 6e6e5a9357ad
Revises: 682d220be62f
Create Date: 2026-03-02 23:21:32.824659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e6e5a9357ad'
down_revision = '682d220be62f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_observations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('target_user_id', sa.Uuid(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.Column('observation', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_observations_id'), 'user_observations', ['id'], unique=False)
    op.create_index(
        op.f('ix_user_observations_target_user_id'),
        'user_observations',
        ['target_user_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_user_observations_owner_id'),
        'user_observations',
        ['owner_id'],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f('ix_user_observations_owner_id'), table_name='user_observations')
    op.drop_index(op.f('ix_user_observations_target_user_id'), table_name='user_observations')
    op.drop_index(op.f('ix_user_observations_id'), table_name='user_observations')
    op.drop_table('user_observations')
