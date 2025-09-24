from .base import SQLModel, Field


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    descricao: str