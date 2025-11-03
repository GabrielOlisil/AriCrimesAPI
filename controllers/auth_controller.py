from fastapi import APIRouter, Depends
from database import SessionDep
from models import Usuario
from services.auth_service import login_or_register, get_current_user, admin_required, get_current_admin_user

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/login", response_model=Usuario)
async def login_or_register_user(
        user: Usuario = Depends(login_or_register)
):
    """
    Recebe o token JWT do Keycloak (via Cabeçalho 'Authorization: Bearer ...'),
    verifica se o usuário existe no banco de dados local.
    - Se não existir, cria um novo usuário.
    - Se existir, atualiza os dados (nome, email, foto) com base no token.
    """
    return user


@router.get("/me")
async def get_my_profile(user_data: Usuario = Depends(get_current_user)):
    """
    Endpoint de teste para verificar se o token JWT é válido e se o
    usuário está autenticado. Retorna uma mensagem de boas-vindas com o nome e ID do usuário.

    """
    return {"message": f"Olá, {user_data.nome}! Seu UID é {user_data.id} e seu acesso está validado."}
