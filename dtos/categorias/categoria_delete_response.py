from pydantic import BaseModel


class CategoriaDeleteResponseDto(BaseModel):
    success: bool
    message: str