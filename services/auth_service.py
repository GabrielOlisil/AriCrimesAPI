from fastapi import Depends, HTTPException, status
from models import Usuario
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth import validate_jwt
from database import SessionDep
from sqlmodel import select

oauth2_scheme = HTTPBearer()

REALM_ROLES_PATH = ["realm_access", "roles"]


def check_role_in_payload(payload: dict, required_role: str, path: list[str]) -> bool:
    """Verifica se uma role está presente no payload, usando um caminho de chaves."""
    current = payload
    try:
        for key in path:
            current = current[key]

        # 'current' agora deve ser a lista de roles
        if isinstance(current, list):
            return required_role in current

    except (KeyError, TypeError):
        # O caminho não existe (ex: não tem realm_access ou roles)
        return False

    return False






def get_validated_token(cred: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = cred.credentials

    try:
        decoded_token = validate_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token do Keycloak inválido ou expirado: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded_token


def role_required(required_role: str):
    """
    Cria uma dependência de FastAPI que verifica se o usuário tem a role necessária.
    """

    def role_checker(user_payload: dict = Depends(get_validated_token)):
        # 1. Verificação de roles do REALM (geralmente onde as roles de ADMIN ficam)
        if check_role_in_payload(user_payload, required_role, REALM_ROLES_PATH):
            return user_payload


        # Se a role não for encontrada, levanta 403
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuário não tem a permissão necessária: '{required_role}'"
        )

    return role_checker


admin_required = role_required("admin")


def login_or_register(
        session: SessionDep,
        token: dict = Depends(get_validated_token)

) -> Usuario:
    uid = token['sub']
    nome = token['name']
    email = token['email']

    picture = None;

    if 'picture' in token:
        picture = token['picture']

    statement = select(Usuario).where(Usuario.keycloak_id == uid)
    db_user = session.exec(statement).first()

    if not db_user:
        # cria o usuario na base
        new_user = Usuario(
            nome=nome,
            email=email,
            keycloak_id=uid,
            profile_pic_url=picture
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    db_user.nome = nome
    db_user.email = email
    db_user.profile_pic_url = picture

    session.commit()
    session.refresh(db_user)

    return db_user


def get_current_user(
        session: SessionDep,
        token: dict = Depends(get_validated_token),
) -> Usuario:
    # nesse ponto, o token é valido

    uid = token['sub']

    statement = select(Usuario).where(Usuario.keycloak_id == uid)
    db_user = session.exec(statement).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário não autenticado')



    return db_user


def get_current_admin_user(
        session: SessionDep,


        token: dict = Depends(admin_required),
) -> Usuario:
    """
    Dependência que:
    1. Verifica se o usuário tem a role 'admin' (usando admin_required).
    2. Busca e retorna o objeto Usuario correspondente no banco de dados.
    """

    uid = token['sub']

    statement = select(Usuario).where(Usuario.keycloak_id == uid)
    db_user = session.exec(statement).first()

    if not db_user:
        # Se um token válido e admin não tiver usuário no DB
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Usuário Admin autenticado no Keycloak, mas não encontrado no sistema.'
        )

    return db_user