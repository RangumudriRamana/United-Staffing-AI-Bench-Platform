"""add active consultant marketing history index

Revision ID: 873b3e6641b9
Revises: a085e3796ba3
Create Date: 2026-09-17 12:31:24.957286

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "873b3e6641b9"
down_revision: Union[str, None] = "a085e3796ba3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_consultant_marketing_history_active_consultant",
        "consultant_marketing_history",
        ["consultant_id"],
        postgresql_where="effective_until IS NULL",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_consultant_marketing_history_active_consultant",
        table_name="consultant_marketing_history",
    )