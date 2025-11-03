from pydantic import BaseModel


class RelatoBatchResponseDto(BaseModel):
    success: bool
    message: str
    created_count: int