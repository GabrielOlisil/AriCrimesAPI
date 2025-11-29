from fastapi import APIRouter
from database import SessionDep
import services.stats_service as stats_service

router = APIRouter(prefix="/stats", tags=["Estatísticas"])

@router.get("/geral")
def get_general_stats(db: SessionDep):
    """Retorna contagem total de relatos e relatos nos últimos 30 dias."""
    return stats_service.get_general_stats(db)

@router.get("/categorias")
def get_category_stats(db: SessionDep):
    """Retorna a quantidade de crimes por categoria."""
    return stats_service.get_stats_by_category(db)