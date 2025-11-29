from datetime import datetime
from typing import TYPE_CHECKING, List, Optional  # <-- ADICIONE

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TSVECTOR

from .base import SQLModel, Field
from sqlmodel import Relationship  # <-- ADICIONE

if TYPE_CHECKING:  # <-- ADICIONE
    from .foto_relato import FotoRelato  # <-- ADICIONE
    from .confirmacao import ConfirmacaoRelato


class Relato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    obj_roubado: str
    descricao: str
    local: str
    latitude: float
    longitude: float
    data_furto: datetime
    data_registro: datetime

    # Novo campo para busca textual (nullable para não quebrar registros)
    # Usamos sa_column para definir tipos específicos do Postgres
    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(TSVECTOR, nullable=True)
    )

    usuario_id: int = Field(foreign_key='usuario.id')
    categoria_id: int = Field(foreign_key='categoria.id')

    # ADICIONE O RELACIONAMENTO ABAIXO
    fotos: List["FotoRelato"] = Relationship(back_populates="relato")

    confirmacoes: List["ConfirmacaoRelato"] = Relationship()

    # 2. Crie a propriedade computada
    @property
    def numero_confirmacoes(self) -> int:
        """Retorna a contagem de confirmações (likes) deste relato."""
        return len(self.confirmacoes)




