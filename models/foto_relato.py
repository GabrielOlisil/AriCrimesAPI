from .base import SQLModel, Field



class FotoRelato(SQLModel, table=True):
    _tablename_ = 'foto_relato'

    id: int | None = Field(default=None, primary_key=True)
    url: str

    relato_id: int = Field(foreign_key='relato.id')