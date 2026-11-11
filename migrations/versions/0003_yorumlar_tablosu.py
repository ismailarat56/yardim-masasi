"""yorumlar tablosu

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-11 16:08:47.256914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "yorumlar",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "talep_id",
            sa.BigInteger(),
            sa.ForeignKey("talepler.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("yazan", sa.Text(), nullable=False),
        sa.Column("metin", sa.Text(), nullable=False),
        sa.Column("yazildi", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("length(trim(yazan)) > 0", name="yorumlar_yazan_check"),
        sa.CheckConstraint("length(trim(metin)) BETWEEN 1 AND 2000", name="yorumlar_metin_check"),
    )
    op.create_index("yorumlar_talep_idx", "yorumlar", ["talep_id", "id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("yorumlar")
