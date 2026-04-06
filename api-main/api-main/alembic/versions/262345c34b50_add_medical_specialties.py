"""add_medical_specialties

Revision ID: 262345c34b50
Revises: c04401d1787e
Create Date: 2026-02-24 19:35:28.987540

"""
from alembic import op
import sqlalchemy as sa


from uuid_utils import uuid7

# revision identifiers, used by Alembic.
revision = '262345c34b50'
down_revision = 'c04401d1787e'
branch_labels = None
depends_on = None

specialties_to_add = [
    "Acupuntura",
    "Alergia e imunologia",
    "Anestesiologia",
    "Angiologia",
    "Cardiologia",
    "Cirurgia cardiovascular",
    "Cirurgia da mão",
    "Cirurgia de cabeça e pescoço",
    "Cirurgia do aparelho digestivo",
    "Cirurgia geral",
    "Cirurgia oncológica",
    "Cirurgia pediátrica",
    "Cirurgia plástica",
    "Cirurgia torácica",
    "Cirurgia vascular",
    "Clínica médica",
    "Coloproctologia",
    "Dermatologia",
    "Endocrinologia e metabologia",
    "Endoscopia",
    "Gastroenterologia",
    "Genética médica",
    "Geriatria",
    "Ginecologia e obstetrícia",
    "Hematologia e hemoterapia",
    "Homeopatia",
    "Infectologia",
    "Mastologia",
    "Medicina de emergência",
    "Medicina de família e comunidade",
    "Medicina do trabalho",
    "Medicina do tráfego",
    "Medicina esportiva",
    "Medicina física e reabilitação",
    "Medicina intensiva",
    "Medicina legal e perícia médica",
    "Medicina nuclear",
    "Medicina preventiva e social",
    "Nefrologia",
    "Neurocirurgia",
    "Neurologia",
    "Nutrologia",
    "Oftalmologia",
    "Oncologia clínica",
    "Ortopedia e traumatologia",
    "Otorrinolaringologia",
    "Patologia",
    "Patologia clínica/medicina laboratorial",
    "Pediatria",
    "Pneumologia",
    "Psiquiatria",
    "Radiologia e diagnóstico por imagem",
    "Radioterapia",
    "Reumatologia",
    "Urologia"
]

def upgrade():
    # We will use raw SQL to insert the specialties linked to the "Médico(a)" profession.
    for specialty in specialties_to_add:
        _id = str(uuid7())
        op.execute(
            f"""
            INSERT INTO specialties (id, profession_id, name, is_active)
            SELECT '{_id}', p.id, '{specialty}', true
            FROM professions p
            WHERE p.name = 'Médico(a)'
            AND NOT EXISTS (
                SELECT 1 FROM specialties WHERE name = '{specialty}' AND profession_id = p.id
            );
            """
        )

def downgrade():
    for specialty in specialties_to_add:
        op.execute(
            f"""
            DELETE FROM specialties
            WHERE name = '{specialty}'
            AND profession_id IN (SELECT id FROM professions WHERE name = 'Médico(a)');
            """
        )
