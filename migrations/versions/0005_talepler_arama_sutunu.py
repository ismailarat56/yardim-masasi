"""talepler arama sutunu

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-12 19:41:37.978645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "talepler",
        sa.Column(
            "arama",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('turkish', baslik)", persisted=True),
        ),
    )
    op.create_index("talepler_arama_idx", "talepler", ["arama"], postgresql_using="gin")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("talepler", "arama")
