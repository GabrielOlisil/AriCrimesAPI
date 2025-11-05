from pydantic import BaseModel

class FotoRelatoRead(BaseModel):
    id: int
    url: str