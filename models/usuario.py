from .base import SQLModel, Field


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    telefone: str | None = None
    endereco: str | None = None
    email: str = Field(unique=True)
    profile_pic_url: str | None = Field(default=None)
    keycloak_id: str = Field(unique=True, index=True)
