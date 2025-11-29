from sqlmodel import Session, select, func, text
from models import Relato, Categoria
from datetime import datetime, timedelta


def get_general_stats(db: Session):
    total_relatos = db.exec(select(func.count(Relato.id))).one()

    data_limite = datetime.now() - timedelta(days=30)
    relatos_30_dias = db.exec(
        select(func.count(Relato.id)).where(Relato.data_furto >= data_limite)
    ).one()

    return {
        "total_geral": total_relatos,
        "total_30_dias": relatos_30_dias
    }


def get_stats_by_category(db: Session):
    # Query agrupada por categoria
    stmt = (
        select(Categoria.nome, func.count(Relato.id))
        .join(Relato, Categoria.id == Relato.categoria_id)
        .group_by(Categoria.nome)
    )
    results = db.exec(stmt).all()

    return [{"categoria": r[0], "quantidade": r[1]} for r in results]