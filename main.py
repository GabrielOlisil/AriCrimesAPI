import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import select
from controllers.categoria_controller import router as categoria_router
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase import load_cred
from firebase_admin import auth
from database import SessionDep

from models import Usuario

cred = load_cred()
app = FastAPI(title="Ari crimes API",
              description="API para gerenciar relatos e categorias.",
              version="0.1.0", )

app.include_router(categoria_router)


@app.get(
    "/healthcheck",
    tags=["healthcheck"],
    responses={
        200: {"content": {
            "application/json": {
                "example": {"status": "ok"}
            }
        },
        }
    })
async def healthcheck():
    return {"status": "ok"}


token_auth_scheme = HTTPBearer()


def get_current_user(
        session: SessionDep,
        creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme)
) -> Usuario:
    token = creds.credentials
    try:
        decoded_token = auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token do Firebase inválido ou expirado: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    uid = decoded_token['user_id']
    if not uid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID do usuário não encontrado no token.")

    # A dependência APENAS busca o usuário. Ela não cria nem atualiza.
    statement = select(Usuario).where(Usuario.google_auth_user_id == uid)
    db_user = session.exec(statement).first()

    if not db_user:
        # Se o usuário não existe no nosso DB, ele não está autorizado a acessar rotas protegidas.
        # Ele precisa primeiro passar pelo endpoint de login.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não registrado. Faça o login primeiro.",
        )

    return db_user


@app.post("/auth/login", response_model=Usuario)
async def login_or_register_user(
        session: SessionDep,
        creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme)
):
    """
    Recebe o Firebase ID Token do cliente (Flutter).
    Valida o token e cria um usuário em nosso banco de dados se for o primeiro login,
    ou atualiza as informações se o usuário já existir.
    """
    token = creds.credentials
    try:
        decoded_token = auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}")

    # Extrai as informações do token decodificado
    uid = decoded_token['user_id']
    email = decoded_token['email']
    nome = decoded_token['name']
    profile_pic = decoded_token['picture']

    # Lógica "Find or Create/Update"
    statement = select(Usuario).where(Usuario.google_auth_user_id == uid)
    db_user = session.exec(statement).first()

    if not db_user:
        print(f"Usuário com UID {uid} não encontrado. Criando novo usuário...")
        db_user = Usuario(
            google_auth_user_id=uid,
            email=email,
            nome=nome,
            profile_pic_url=profile_pic
        )
        session.add(db_user)
    else:
        print(f"Usuário com UID {uid} encontrado. Atualizando informações...")
        db_user.nome = nome
        db_user.profile_pic_url = profile_pic
        session.add(db_user)

    session.commit()
    session.refresh(db_user)

    return db_user


@app.get("/users/me")
async def get_my_profile(user_data: Usuario = Depends(get_current_user)):

    return {"message": f"Olá, {user_data.nome}! Seu UID é {user_data.id} e seu acesso está validado."}
