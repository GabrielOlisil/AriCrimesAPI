from sqlmodel import SQLModel, Field
from datetime import datetime


class ConfirmacaoRelato(SQLModel, table=True):
    __tablename__ = "confirmacao_relato"

    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    relato_id: int = Field(foreign_key="relato.id", primary_key=True)
    data_confirmacao: datetime = Field(default_factory=datetime.now)