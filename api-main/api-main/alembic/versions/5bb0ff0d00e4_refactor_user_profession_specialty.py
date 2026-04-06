"""refactor_user_profession_specialty

Revision ID: 5bb0ff0d00e4
Revises: 262345c34b50
Create Date: 2026-02-24 19:53:45.944984

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5bb0ff0d00e4'
down_revision = '262345c34b50'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add profession_id to users
    op.add_column('users', sa.Column('profession_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_users_profession_id'), 'users', ['profession_id'], unique=False)
    op.create_foreign_key('fk_users_profession_id', 'users', 'professions', ['profession_id'], ['id'], ondelete='SET NULL')

    # 2. Migrate data
    op.execute("UPDATE users SET profession_id = ups.profession_id FROM user_professions_specialties ups WHERE users.id = ups.user_id AND ups.is_primary = true")
    op.execute("UPDATE users SET profession_id = ups.profession_id FROM user_professions_specialties ups WHERE users.id = ups.user_id AND users.profession_id IS NULL")

    # 3. Clean up old indexes and constraints
    op.drop_index(op.f('ix_user_professions_specialties_id'), table_name='user_professions_specialties')
    op.drop_index(op.f('ix_user_professions_specialties_profession_id'), table_name='user_professions_specialties')
    op.drop_index(op.f('ix_user_professions_specialties_specialty_id'), table_name='user_professions_specialties')
    op.drop_index(op.f('ix_user_professions_specialties_user_id'), table_name='user_professions_specialties')

    op.drop_constraint('user_professions_specialties_profession_id_fkey', 'user_professions_specialties', type_='foreignkey')
    op.drop_constraint('user_professions_specialties_specialty_id_fkey', 'user_professions_specialties', type_='foreignkey')
    op.drop_constraint('user_professions_specialties_user_id_fkey', 'user_professions_specialties', type_='foreignkey')
    op.drop_constraint('uq_user_profession_specialty', 'user_professions_specialties', type_='unique')
    op.drop_constraint('user_professions_specialties_pkey', 'user_professions_specialties', type_='primary')

    # 4. Filter records with null specialty_id since we will make it non-nullable (or delete them if they only existed for profession)
    op.execute("DELETE FROM user_professions_specialties WHERE specialty_id IS NULL")

    # 5. Drop profession_id column and alter specialty_id to non-nullable
    op.drop_column('user_professions_specialties', 'profession_id')
    op.alter_column('user_professions_specialties', 'specialty_id', existing_type=sa.UUID(), nullable=False)

    # 6. Rename table
    op.rename_table('user_professions_specialties', 'user_specialties')

    # 7. Recreate constraints and indexes
    op.create_primary_key('user_specialties_pkey', 'user_specialties', ['id'])
    op.create_foreign_key('fk_user_specialties_specialty_id', 'user_specialties', 'specialties', ['specialty_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_user_specialties_user_id', 'user_specialties', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uq_user_specialty', 'user_specialties', ['user_id', 'specialty_id'])

    op.create_index(op.f('ix_user_specialties_id'), 'user_specialties', ['id'], unique=False)
    op.create_index(op.f('ix_user_specialties_specialty_id'), 'user_specialties', ['specialty_id'], unique=False)
    op.create_index(op.f('ix_user_specialties_user_id'), 'user_specialties', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_specialties_user_id'), table_name='user_specialties')
    op.drop_index(op.f('ix_user_specialties_specialty_id'), table_name='user_specialties')
    op.drop_index(op.f('ix_user_specialties_id'), table_name='user_specialties')

    op.drop_constraint('uq_user_specialty', 'user_specialties', type_='unique')
    op.drop_constraint('fk_user_specialties_user_id', 'user_specialties', type_='foreignkey')
    op.drop_constraint('fk_user_specialties_specialty_id', 'user_specialties', type_='foreignkey')
    op.drop_constraint('user_specialties_pkey', 'user_specialties', type_='primary')

    op.rename_table('user_specialties', 'user_professions_specialties')

    op.alter_column('user_professions_specialties', 'specialty_id', existing_type=sa.UUID(), nullable=True)
    op.add_column('user_professions_specialties', sa.Column('profession_id', sa.UUID(), autoincrement=False, nullable=True))
    op.execute("UPDATE user_professions_specialties ups SET profession_id = users.profession_id FROM users WHERE users.id = ups.user_id")
    # Setting it to false only where null isn't perfectly reversable but we just enforce rule
    op.execute("UPDATE user_professions_specialties SET profession_id = (SELECT id FROM professions LIMIT 1) WHERE profession_id IS NULL")
    op.alter_column('user_professions_specialties', 'profession_id', existing_type=sa.UUID(), nullable=False)

    op.create_primary_key('user_professions_specialties_pkey', 'user_professions_specialties', ['id'])
    op.create_unique_constraint('uq_user_profession_specialty', 'user_professions_specialties', ['user_id', 'profession_id', 'specialty_id'])
    op.create_foreign_key('user_professions_specialties_user_id_fkey', 'user_professions_specialties', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_professions_specialties_specialty_id_fkey', 'user_professions_specialties', 'specialties', ['specialty_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('user_professions_specialties_profession_id_fkey', 'user_professions_specialties', 'professions', ['profession_id'], ['id'], ondelete='CASCADE')

    op.create_index(op.f('ix_user_professions_specialties_user_id'), 'user_professions_specialties', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_professions_specialties_specialty_id'), 'user_professions_specialties', ['specialty_id'], unique=False)
    op.create_index(op.f('ix_user_professions_specialties_profession_id'), 'user_professions_specialties', ['profession_id'], unique=False)
    op.create_index(op.f('ix_user_professions_specialties_id'), 'user_professions_specialties', ['id'], unique=False)

    op.drop_constraint('fk_users_profession_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_profession_id'), table_name='users')
    op.drop_column('users', 'profession_id')
