"""add_postgis_index_to_relato

Revision ID: 13236d446ccf
Revises: 71f85339cdfc
Create Date: 2025-11-03 14:04:25.630164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '13236d446ccf'
down_revision: Union[str, Sequence[str], None] = '71f85339cdfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Adiciona a nova coluna 'localizacao_geog'
    # Esta coluna será do tipo 'geography' e será *calculada* automaticamente
    # a partir de 'longitude' e 'latitude' sempre que um relato for inserido ou atualizado.
    op.add_column(
        'relato',
        sa.Column(
            'localizacao_geog',
            geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, spatial_index=False),
            sa.Computed(
                'ST_MakePoint(longitude, latitude)::geography',
                persisted=True  # 'STORED' no PostgreSQL, essencial para indexar
            ),
            nullable=True  # Permitir nulo por segurança, embora lat/lon sejam obrigatórios
        )
    )

    # 3. Cria o índice espacial GiST na nova coluna gerada.
    # É isso que torna a busca por raio/proximidade extremamente rápida.
    op.create_index(
        'ix_relato_localizacao_geog_gist',
        'relato',
        ['localizacao_geog'],
        unique=False,
        postgresql_using='gist'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_relato_localizacao_geog_gist', table_name='relato')

    # 2. Remove a coluna
    op.drop_column('relato', 'localizacao_geog')
