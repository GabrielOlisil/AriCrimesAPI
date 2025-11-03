from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from starlette.middleware.cors import CORSMiddleware

from controllers.categoria_controller import router as categoria_router
from controllers.auth_controller import router as auth_router
from controllers.relato_controller import router as relato_router
from controllers.heatmap_controller import router as heatmap_router

from auth import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Aplicação iniciando... buscando cliente JWKS do Keycloak.")
    auth.jwks_client = auth.get_jwks_client()
    print("✅ Cliente JWKS pronto.")

    yield

    print("👋 Aplicação encerrada.")


servers = [
    {
        "url": "http://localhost:8000/",
        "description": "Ambiente de Desenvolvimento"
    },
    {
        "url": "https://aricrimes-api.gabiruka.duckdns.org/",
        "description": "Ambiente de Produçãoo"
    },

]

origins = [
    "*",
]

app = FastAPI(title="Ari crimes API",
              description="API para gerenciar relatos e categorias.",
              version="0.1.0",
              servers=servers,
              lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

app.include_router(categoria_router)
app.include_router(auth_router)
app.include_router(relato_router)

app.include_router(heatmap_router)


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
    """
    Endpoint simples para verificar se a API está online e respondendo.
    Usado por serviços de monitoramento (como o CapRover) para saber se a aplicação está "viva".
    """
    return {"status": "ok"}
