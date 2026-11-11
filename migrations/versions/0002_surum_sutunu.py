"""surum sutunu

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-11 15:04:42.716810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "talepler",
        sa.Column("surum", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_check_constraint("talepler_surum_check", "talepler", "surum >= 1")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("talepler", "surum")
