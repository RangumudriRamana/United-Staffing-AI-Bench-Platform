"""add submission foreign key indexes

Revision ID: a085e3796ba3
Revises: 02287fd554ef
Create Date: 2026-09-17 12:05:58.261095

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a085e3796ba3"
down_revision: Union[str, None] = "02287fd554ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_submissions_client_id",
        "submissions",
        ["client_id"],
    )
    op.create_index(
        "ix_submissions_requirement_id",
        "submissions",
        ["requirement_id"],
    )
    op.create_index(
        "ix_submissions_vendor_id",
        "submissions",
        ["vendor_id"],
    )
    op.create_index(
        "ix_submissions_vendor_contact_id",
        "submissions",
        ["vendor_contact_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_submissions_vendor_contact_id",
        table_name="submissions",
    )
    op.drop_index(
        "ix_submissions_vendor_id",
        table_name="submissions",
    )
    op.drop_index(
        "ix_submissions_requirement_id",
        table_name="submissions",
    )
    op.drop_index(
        "ix_submissions_client_id",
        table_name="submissions",
    )