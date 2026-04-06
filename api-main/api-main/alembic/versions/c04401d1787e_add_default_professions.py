"""add_default_professions

Revision ID: c04401d1787e
Revises: 4137230aa97b
Create Date: 2026-02-24 19:19:17.442133

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from uuid_utils import uuid7



import uuid

# revision identifiers, used by Alembic.
revision = 'c04401d1787e'
down_revision = '4137230aa97b'
branch_labels = None
depends_on = None

professions_to_add = [
    "Médico(a)",
    "Assistente Social",
    "Auxiliar de Enfermagem",
    "Biomédico(a)",
    "Dentista (Cirurgião-dentista)",
    "Educador(a) Físico(a)",
    "Enfermeiro(a)",
    "Farmacêutico(a)",
    "Fisioterapeuta",
    "Fonoaudiólogo(a)",
    "Médico(a) Veterinário(a)",
    "Nutricionista",
    "Psicólogo(a)",
    "Sanitarista (Saúde Coletiva)",
    "Técnico(a) de Enfermagem",
    "Técnico(a) em Análises Clínicas",
    "Técnico(a) em Prótese Dentária",
    "Técnico(a) em Radiologia",
    "Técnico(a) em Saúde Bucal",
    "Terapeuta Ocupacional",
    "Outro",
]


def upgrade():
    for profession in professions_to_add:
        _id = str(uuid7())
        op.execute(
            f"""
            INSERT INTO professions (id, name, is_active)
            SELECT '{_id}', '{profession}', true
            WHERE NOT EXISTS (
                SELECT 1 FROM professions WHERE name = '{profession}'
            );
            """
        )


def downgrade():
    for profession in professions_to_add:
        op.execute(
            f"DELETE FROM professions WHERE name = '{profession}';"
        )
