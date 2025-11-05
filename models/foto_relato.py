from .base import SQLModel, Field
from typing import TYPE_CHECKING  # <-- ADICIONE
from sqlmodel import Relationship  # <-- ADICIONE

if TYPE_CHECKING:  # <-- ADICIONE
    from .relato import Relato  # <-- ADICIONE


class FotoRelato(SQLModel, table=True):
    # Garante que o nome da tabela seja 'fotorelato'
    __tablename__ = 'fotorelato'

    id: int | None = Field(default=None, primary_key=True)
    url: str

    relato_id: int = Field(foreign_key='relato.id')

    # ADICIONE O RELACIONAMENTO ABAIXO
    relato: "Relato" = Relationship(back_populates="fotos")