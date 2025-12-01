from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException
from dtos.relatos.relato_delete_response import RelatoDeleteResponseDto
from dtos import RelatoCreateDto
from database import SessionDep
from dtos.relatos.relato_batch_response import RelatoBatchResponseDto
from models import Relato, Usuario
from services.auth_service import get_current_user, get_current_admin_user
import services.relato_service as relato_service
from dtos import RelatoRead
from datetime import datetime
from services.relato_service import toggle_confirmacao, search_relatos
from services.auth_service import get_validated_token, check_role_in_payload, REALM_ROLES_PATH

router = APIRouter(prefix="/relato", tags=["Relato"])

@router.post("", response_model=Relato, status_code=status.HTTP_201_CREATED)
async def create_relato(relato: RelatoCreateDto, session: SessionDep, user = Depends(get_current_user)):
    """
    Cria um novo relato de crime. O relato é automaticamente
    associado ao usuário que está autenticado via token JWT.

    """
    return relato_service.create_relato(relato, user, session)


@router.get("", response_model=list[RelatoRead])
async def get_all_relatos(db: SessionDep, offset: int=0, limit:  Annotated[int, Query(le=100)] = 100):
    """

    Retorna uma lista paginada de todos os relatos no sistema,
    independentemente do usuário.

    """

    return relato_service.get_all_relatos(db, offset, limit)


@router.get("/my", response_model=list[RelatoRead])
async def get_my_relatos(
        db: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 10,
        user: Usuario = Depends(get_current_user)

):
    """Pega os últimos relatos registrados, ordenados por data de registro."""
    return relato_service.get_my_relatos(db, offset, limit, user.id)


@router.get("/latest", response_model=list[RelatoRead])
async def get_latest_relatos(
        db: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 10
):
    """Pega os últimos relatos registrados, ordenados por data de registro."""
    return relato_service.get_latest_relatos(db, offset, limit)


@router.get("/nearby", response_model=list[RelatoRead])
async def get_relatos_nearby(
        db: SessionDep,
        lat: float = Query(..., description="Latitude do ponto central", example=-9.9740),
        lon: float = Query(..., description="Longitude do ponto central", example=-63.0331),
        radius: float = Query(2.0, description="Raio em Km (max 50)", gt=0, le=50),
):
    """Busca relatos em um raio (em Km) de um ponto central."""
    return relato_service.get_relatos_nearby(db=db, latitude=lat, longitude=lon, radius_km=radius)


@router.get("/{relato_id}", response_model=RelatoRead)
async def get_relato_by_id(relato_id: int, db: SessionDep):
    """Pega um relato específico pelo ID."""
    relato = relato_service.get_relato_by_id(db, relato_id)
    if not relato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relato não encontrado")
    return relato


@router.put("/{relato_id}", response_model=Relato)
async def update_relato(
        relato_id: int,
        relato_data: RelatoCreateDto,  # Reutilizando o DTO de criação para o PUT
        db: SessionDep,
        user: Usuario = Depends(get_current_user)
):
    """
    Atualiza um relato.
    Apenas o usuário que criou o relato pode atualizá-lo.
    """
    updated_relato = relato_service.update_relato(db, relato_id, relato_data, user)

    if not updated_relato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relato não encontrado")

    # Se o usuário não for o dono, o service levantará um 403 Forbidden
    return updated_relato


@router.delete("/{relato_id}", response_model=RelatoDeleteResponseDto)
async def delete_relato(
        relato_id: int,
        db: SessionDep,
        user: Usuario = Depends(get_current_user),
        token_payload: dict = Depends(get_validated_token)
):
    """
    Deleta um relato.
    Apenas o usuário que criou o relato pode deletá-lo.
    """

    is_admin = check_role_in_payload(token_payload, "admin", REALM_ROLES_PATH)
    try:
        success = relato_service.delete_relato(db, relato_id, user, is_admin=is_admin)
        if not success:
            # Se retornou False (e não um 403), é porque não foi encontrado
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relato não encontrado")

    except HTTPException as e:
        # Repassa exceções (como 403 Forbidden do service)
        raise e
    except Exception as e:
        # Captura erros gerais
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return RelatoDeleteResponseDto(success=True, message="Relato deletado com sucesso")


@router.post("/batch", response_model=RelatoBatchResponseDto, status_code=status.HTTP_201_CREATED)
async def create_relatos_batch(
        relatos_data: list[RelatoCreateDto],
        db: SessionDep,
        admin_user: Usuario = Depends(get_current_admin_user)  # <-- Protegido por Admin
):
    """
    Cria múltiplos relatos em um único lote.
    Acessível apenas por administradores.
    Todos os relatos criados serão associados ao admin que fez o upload.
    """
    created_count = relato_service.create_relatos_batch(
        relatos_data=relatos_data,
        admin_user=admin_user,
        db=db
    )

    return RelatoBatchResponseDto(
        success=True,
        message=f"{created_count} relatos criados com sucesso.",
        created_count=created_count
    )



# 1. Endpoint: Filtrar por Categoria
@router.get("/categoria/{category_id}", response_model=list[RelatoRead])
async def get_relatos_por_categoria(
    category_id: int,
    db: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    """
    Retorna relatos filtrados por uma categoria específica.
    """
    relatos = relato_service.get_relatos_by_category(db, category_id, offset, limit)
    return relatos


# 2. Endpoint: Filtrar por Usuário (ID específico)
@router.get("/usuario/{user_id}", response_model=list[RelatoRead])
async def get_relatos_por_usuario(
    user_id: int,
    db: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    """
    Retorna todos os relatos feitos por um usuário específico (pelo ID do usuário).
    """
    relatos = relato_service.get_relatos_by_user_id(db, user_id, offset, limit)
    return relatos


# 3. Endpoint: Filtrar por Intervalo de Datas
@router.get("/busca/periodo", response_model=list[RelatoRead])
async def get_relatos_por_periodo(
    db: SessionDep,
    start_date: datetime = Query(..., description="Data inicial (ISO 8601), ex: 2025-01-01T00:00:00"),
    end_date: datetime = Query(..., description="Data final (ISO 8601), ex: 2025-01-31T23:59:59"),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    """
    Retorna relatos ocorridos dentro de um intervalo de datas (baseado na data_furto).
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data inicial não pode ser maior que a data final."
        )

    relatos = relato_service.get_relatos_by_date_range(db, start_date, end_date, offset, limit)
    return relatos


@router.post("/{relato_id}/confirmar", status_code=status.HTTP_200_OK)
async def confirmar_relato(
    relato_id: int,
    db: SessionDep,
    user: Usuario = Depends(get_current_user)
):
    """
    Alterna (toggle) a confirmação de um relato.
    Funciona como um 'Upvote' ou 'Eu também vi'.
    """
    return toggle_confirmacao(db, relato_id, user)

@router.get("/search/text", response_model=list[RelatoRead])
async def buscar_relatos_texto(
    q: str,
    db: SessionDep,
    offset: int = 0,
    limit: int = 100
):
    """
    Realiza uma busca textual (Full Text Search) nos relatos.
    Procura no objeto roubado e descrição.
    """
    return search_relatos(db, q, offset, limit)