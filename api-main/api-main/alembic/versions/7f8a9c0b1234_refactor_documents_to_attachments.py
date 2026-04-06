"""Refactor documents to attachments

Revision ID: 7f8a9c0b1234
Revises: 6d659bbb2629
Create Date: 2026-02-18 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f8a9c0b1234"
down_revision = "6d659bbb2629"
branch_labels = None
depends_on = None


def upgrade():
    # Rename table
    op.rename_table("documents", "attachments")

    # Drop old index
    op.drop_index("ix_documents_id", table_name="attachments")

    # Drop columns that won't be needed
    op.drop_column("attachments", "code")
    op.drop_column("attachments", "uf")
    op.drop_column("attachments", "source")
    op.drop_column("attachments", "issuing_body")
    op.drop_column("attachments", "issuing_date")
    op.drop_column("attachments", "expiration_date")

    # Rename file_url to url
    op.alter_column("attachments", "file_url", new_column_name="url")

    # Add title column
    op.add_column(
        "attachments",
        sa.Column("title", sa.String(length=255), nullable=False, server_default="Untitled"),
    )

    # Remove server_default after adding the column
    op.alter_column("attachments", "title", server_default=None)

    # Create new index
    op.create_index(op.f("ix_attachments_id"), "attachments", ["id"], unique=False)


def downgrade():
    # Drop new index
    op.drop_index(op.f("ix_attachments_id"), table_name="attachments")

    # Remove title column
    op.drop_column("attachments", "title")

    # Rename url back to file_url
    op.alter_column("attachments", "url", new_column_name="file_url")

    # Add back dropped columns
    op.add_column("attachments", sa.Column("code", sa.String(length=50), nullable=True))
    op.add_column("attachments", sa.Column("uf", sa.String(length=2), nullable=True))
    op.add_column(
        "attachments",
        sa.Column(
            "source",
            sa.Enum(
                "RG",
                "CNH",
                "CRM",
                "CNS",
                "SUS",
                "VACCINATION_CARD",
                "PROOF_OF_ADDRESS",
                name="documentsourceenum",
            ),
            nullable=True,
        ),
    )
    op.add_column("attachments", sa.Column("issuing_body", sa.String(length=255), nullable=True))
    op.add_column("attachments", sa.Column("issuing_date", sa.Date(), nullable=True))
    op.add_column("attachments", sa.Column("expiration_date", sa.Date(), nullable=True))

    # Create old index
    op.create_index("ix_documents_id", "attachments", ["id"], unique=False)

    # Rename table back
    op.rename_table("attachments", "documents")
