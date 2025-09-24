from datetime import datetime

from .base import SQLModel, Field



class Relato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    obj_roubado: str
    descricao: str
    local: str
    latitude: float
    longitude: float
    data_furto: datetime
    data_registro: datetime

    usuario_id: int =  Field(foreign_key='usuario.id')
    categoria_id: int =  Field(foreign_key='categoria.id')