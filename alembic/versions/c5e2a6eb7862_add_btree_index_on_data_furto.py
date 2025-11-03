"""add_btree_index_on_data_furto

Revision ID: c5e2a6eb7862
Revises: 13236d446ccf
Create Date: 2025-11-03 17:20:27.852097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c5e2a6eb7862'
down_revision: Union[str, Sequence[str], None] = '13236d446ccf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f('ix_relato_data_furto'),
        'relato',
        ['data_furto'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_relato_data_furto'), table_name='relato')
