from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from controllers.categoria_controller import router as categoria_router
from controllers.auth_controller import router as auth_router

from auth import auth


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Aplicação iniciando... buscando cliente JWKS do Keycloak.")
    auth.jwks_client = auth.get_jwks_client()
    print("✅ Cliente JWKS pronto.")

    yield


    print("👋 Aplicação encerrada.")

app = FastAPI(title="Ari crimes API",
              description="API para gerenciar relatos e categorias.",
              version="0.1.0",

              lifespan=lifespan)

app.include_router(categoria_router)
app.include_router(auth_router)


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


