import requests
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

KEYCLOAK_SERVER_URL = "https://kc.gabiruka.duckdns.org"
KEYCLOAK_REALM = "aricrimes"
KEYCLOAK_CLIENT_ID = "flutter-app"


WELL_KNOWN_URL = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration"


jwks_client: jwt.PyJWKClient | None = None




def get_jwks_client():
    """
    Busca o documento de descoberta, encontra a URL do JWKS e retorna um
    cliente PyJWKClient que busca e armazena as chaves em cache.
    """
    try:
        oidc_config = requests.get(WELL_KNOWN_URL).json()
        jwks_uri = oidc_config["jwks_uri"]

        return jwt.PyJWKClient(jwks_uri)
    except requests.exceptions.RequestException as e:
        # Em um app real, adicione logging aqui
        raise Exception(f"Não foi possível conectar ao Keycloak para obter a configuração OIDC: {e}")




def validate_jwt(token: str) -> dict:
    """
    Valida um token JWT do Keycloak usando PyJWT de forma universal.
    """
    try:
        # 1. Pega o 'kid' (Key ID) do cabeçalho do token
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # 2. Decodifica e valida o token
        # Esta única chamada faz tudo:
        # - Verifica a assinatura com a chave pública correta
        # - Verifica a expiração
        # - Verifica o 'issuer'
        # - Verifica o 'audience'
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],  # Algoritmo usado pelo Keycloak
            audience=KEYCLOAK_CLIENT_ID,
            issuer=f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"
        )
        return payload

    # Captura exceções específicas para dar erros mais claros
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Audience (público-alvo) do token inválido.")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Issuer (emissor) do token inválido.")
    except jwt.PyJWTError as e:
        # Erro genérico da biblioteca
        raise HTTPException(status_code=401, detail=f"Erro de validação do token: {e}")
    except Exception as e:
        # Outros erros (ex: falha de rede ao buscar chaves)
        raise HTTPException(status_code=500, detail=f"Erro interno ao validar o token: {e}")



