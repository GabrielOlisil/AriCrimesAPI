from pydantic import BaseModel


class RelatoDeleteResponseDto(BaseModel):
    success: bool
    message: str