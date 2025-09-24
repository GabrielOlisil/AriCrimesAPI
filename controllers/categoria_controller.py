from fastapi import APIRouter, Query, status, HTTPException

import services.categoria_service as categoria_service
from database import SessionDep
from dtos import CategoriaCreateDto, CategoriaDeleteResponseDto
from models import Categoria
from typing import Annotated

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/", response_model=list[Categoria])
def get_categorias(session: SessionDep, offset: int=0, limit: Annotated[int, Query(le=100)] = 100):
    return categoria_service.get_all_categorias(db=session, offset=offset, limit=limit)


@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def create_categoria(categoria: CategoriaCreateDto, session: SessionDep):
    return categoria_service.create_categoria(categoria, db=session)

@router.put("/{cat_id}", response_model=Categoria)
def update_categoria(categoria: CategoriaCreateDto, cat_id: int, session: SessionDep):
    operation = categoria_service.try_update_categorias(db=session, id=cat_id, categoria=categoria)

    if operation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria not found")

    return operation


@router.delete("/{cat_id}", response_model=CategoriaDeleteResponseDto)
def delete_categoria(cat_id: int,session: SessionDep):
    operation = categoria_service.try_delete_categoria(db=session, id=cat_id)
    if not operation:
         return CategoriaDeleteResponseDto(success=False, message="Categoria not deleted")

    return CategoriaDeleteResponseDto(success=True, message="Categoria deleted")

