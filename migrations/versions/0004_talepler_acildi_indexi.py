"""talepler acildi indexi

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-12 18:59:32.494293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index("talepler_acildi_id_idx", "talepler", ["acildi", "id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("talepler_acildi_id_idx", table_name="talepler")
