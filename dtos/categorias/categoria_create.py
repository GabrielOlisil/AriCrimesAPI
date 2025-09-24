from pydantic import BaseModel


class CategoriaCreateDto(BaseModel):
    nome: str
    descricao: str