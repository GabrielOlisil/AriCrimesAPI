from pydantic import BaseModel


class RelatoCreateDto(BaseModel):
    obj_roubado: str
    descricao: str
    local: str
    latitude: float
    longitude: float
    data_furto: str
    data_registro: str

    categoria_id: int