"""add_professional_crm_table

Revision ID: be698ae17eb7
Revises: 7f8a9c0b1234
Create Date: 2026-02-18 21:57:04.546705

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "be698ae17eb7"
down_revision = "7f8a9c0b1234"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "professional_crm",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_professional_crm_id"), "professional_crm", ["id"], unique=False)
    op.create_index(
        op.f("ix_professional_crm_user_id"), "professional_crm", ["user_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_professional_crm_user_id"), table_name="professional_crm")
    op.drop_index(op.f("ix_professional_crm_id"), table_name="professional_crm")
    op.drop_table("professional_crm")
