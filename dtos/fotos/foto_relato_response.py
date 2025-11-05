from pydantic import BaseModel

class FotoRelatoResponseDto(BaseModel):
    id: int
    url: str
    relato_id: int