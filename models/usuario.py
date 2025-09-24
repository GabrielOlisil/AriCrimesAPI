from .base import SQLModel, Field


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    telefone: str | None = None
    endereco: str | None = None
    email: str = Field(unique=True)
    google_auth_user_id:  str = Field(unique=True, index=True)
    senha: str | None = None
    profile_pic_url: str | None = Field(default=None)