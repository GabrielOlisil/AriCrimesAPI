from fastapi import APIRouter, Depends

from dtos import RelatoCreateDto
from database import SessionDep
from models import Relato
from services.auth_service import get_current_user
import services.relato_service as relato_service

router = APIRouter(prefix="/relato", tags=["Relato"])

@router.post("/")
async def create_relato(relato: RelatoCreateDto, session: SessionDep, user = Depends(get_current_user)):
    return relato_service.create_relato(relato, user, session)


@router.get("/")
async def get_all_relatos(db: SessionDep, offset: int, limit: int):
    return relato_service.get_all_relatos(db, offset, limit)