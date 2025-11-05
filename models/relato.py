from datetime import datetime
from typing import TYPE_CHECKING, List  # <-- ADICIONE
from .base import SQLModel, Field
from sqlmodel import Relationship  # <-- ADICIONE

if TYPE_CHECKING:  # <-- ADICIONE
    from .foto_relato import FotoRelato  # <-- ADICIONE


class Relato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    obj_roubado: str
    descricao: str
    local: str
    latitude: float
    longitude: float
    data_furto: datetime
    data_registro: datetime

    usuario_id: int = Field(foreign_key='usuario.id')
    categoria_id: int = Field(foreign_key='categoria.id')

    # ADICIONE O RELACIONAMENTO ABAIXO
    fotos: List["FotoRelato"] = Relationship(back_populates="relato")

