from pydantic import BaseModel


class UserCreateDto(BaseModel):
    nome: str
    telefone: str | None
    endereco: str | None
    email: str
    google_auth_user_id:  str
    senha: str | None
    profile_pic_url: str | None