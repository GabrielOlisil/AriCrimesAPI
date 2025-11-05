from datetime import datetime
from typing import List
from sqlmodel import SQLModel
from ..fotos.foto_relato_read import FotoRelatoRead


# Este é o nosso novo modelo de resposta.
# É uma classe Pydantic/SQLModel que espelha o Relato,
# mas define explicitamente que 'fotos' deve ser uma lista de 'FotoRelatoRead'.
class RelatoRead(SQLModel):
    id: int
    obj_roubado: str
    descricao: str
    local: str
    latitude: float
    longitude: float
    data_furto: datetime
    data_registro: datetime
    usuario_id: int
    categoria_id: int

    # Este campo irá conter a lista de URLs das fotos
    fotos: List[FotoRelatoRead] = []