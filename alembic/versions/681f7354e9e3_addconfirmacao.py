"""AddConfirmacao

Revision ID: 681f7354e9e3
Revises: c5e2a6eb7862
Create Date: 2025-11-28 19:53:41.732094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '681f7354e9e3'
down_revision: Union[str, Sequence[str], None] = 'c5e2a6eb7862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Criar tabela de confirmações
    op.create_table('confirmacao_relato',
                    sa.Column('usuario_id', sa.Integer(), nullable=False),
                    sa.Column('relato_id', sa.Integer(), nullable=False),
                    sa.Column('data_confirmacao', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['relato_id'], ['relato.id'], ),
                    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
                    sa.PrimaryKeyConstraint('usuario_id', 'relato_id')
                    )

    # 2. Adicionar campo de busca (nullable)
    op.add_column('relato', sa.Column('search_vector', TSVECTOR(), nullable=True))

    # 3. Criar índice GIN para busca rápida
    op.create_index('ix_relato_search_vector', 'relato', ['search_vector'], unique=False, postgresql_using='gin')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_relato_search_vector', table_name='relato', postgresql_using='gin')
    op.drop_column('relato', 'search_vector')
    op.drop_table('confirmacao_relato')
    pass
