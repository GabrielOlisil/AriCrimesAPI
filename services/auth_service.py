from fastapi import Depends, HTTPException, status
from models import Usuario
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth import validate_jwt
from database import SessionDep
from sqlmodel import select


oauth2_scheme = HTTPBearer()



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


def get_current_user(
        session: SessionDep,
        token: dict = Depends(get_validated_token),
) -> Usuario:
    # nesse ponto, o token é valido

    uid = token['sub']
    nome = token['name']
    email = token['email']
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