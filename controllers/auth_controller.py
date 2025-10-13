from fastapi import APIRouter, Depends
from database import SessionDep
from models import Usuario
from services.auth_service import login_or_register, get_current_user, admin_required, get_current_admin_user

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/login", response_model=Usuario)
async def login_or_register_user(
        user: Usuario = Depends(login_or_register)
):
    return user


@router.get("/me")
async def get_my_profile(user_data: Usuario = Depends(get_current_user)):
    return {"message": f"Olá, {user_data.nome}! Seu UID é {user_data.id} e seu acesso está validado."}
