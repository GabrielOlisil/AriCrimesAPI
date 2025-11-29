from typing import Sequence

from fastapi import HTTPException, status

from dtos import RelatoCreateDto
from sqlmodel import Session, select, text
from models import Relato, Usuario, ConfirmacaoRelato
from sqlalchemy.orm import selectinload
from datetime import datetime

def create_relato(relato: RelatoCreateDto, user: Usuario, db: Session):
    try:
        db_relato = Relato(**relato.model_dump())

        db_relato.usuario_id = user.id

        db.add(db_relato)
        db.commit()
        db.refresh(db_relato)

        # Atualiza o search_vector via SQL puro para garantir a sintaxe correta do Postgres
        stmt = text("""
                    UPDATE relato
                    SET search_vector = to_tsvector('portuguese', :texto)
                    WHERE id = :id
                    """)
        texto_busca = f"{db_relato.obj_roubado} {db_relato.descricao}"
        db.exec(stmt, {"texto": texto_busca, "id": db_relato.id})
        db.commit()


        return db_relato
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao criar o relato {e}')


def toggle_confirmacao(db: Session, relato_id: int, user: Usuario):
    relato = db.get(Relato, relato_id)
    if not relato:
        raise HTTPException(status_code=404, detail="Relato não encontrado")

    # Verifica se já existe confirmação
    stmt = select(ConfirmacaoRelato).where(
        ConfirmacaoRelato.relato_id == relato_id,
        ConfirmacaoRelato.usuario_id == user.id
    )
    existing = db.exec(stmt).first()

    if existing:
        # Se existe, remove (toggle off)
        db.delete(existing)
        db.commit()
        return {"message": "Confirmação removida", "confirmed": False}
    else:
        # Se não existe, cria (toggle on)
        nova_conf = ConfirmacaoRelato(relato_id=relato_id, usuario_id=user.id)
        db.add(nova_conf)
        db.commit()
        return {"message": "Ocorrência confirmada", "confirmed": True}


def search_relatos(db: Session, query_text: str, offset: int, limit: int) -> Sequence[Relato]:
    # Usa o operador @@ do Postgres para Full Text Search
    stmt = (
        select(Relato)
        .where(text("search_vector @@ plainto_tsquery('portuguese', :q)"))
        .params(q=query_text)
        .options(
            selectinload(Relato.fotos),
            selectinload(Relato.confirmacoes)
        )
        .offset(offset)
        .limit(limit)
    )
    return db.exec(stmt).all()

def get_all_relatos(db: Session, offset: int, limit: int) -> Sequence[Relato]:
    query = (
        select(Relato)
        .options(
            selectinload(Relato.fotos),
            selectinload(Relato.confirmacoes)  # <-- Carrega a lista para podermos contar
        )
        .offset(offset)
        .limit(limit)
    )
    relatos = db.exec(query).all()
    return relatos


def get_relato_by_id(db: Session, relato_id: int) -> Relato | None:
    """Busca um relato específico pelo ID."""
    query = (
        select(Relato)
        .where(Relato.id == relato_id)
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
    )
    relato = db.exec(query).first()
    return relato


def update_relato(db: Session, relato_id: int, relato_data: RelatoCreateDto, user: Usuario) -> Relato | None:
    """
    Atualiza um relato.
    Apenas o proprietário do relato pode atualizá-lo.
    """
    db_relato = db.get(Relato, relato_id)

    if not db_relato:
        return None

    # Regra de negócio: Apenas o usuário que criou o relato pode atualizá-lo
    if db_relato.usuario_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Usuário não autorizado a modificar este relato")

    # Atualiza os campos do DTO
    relato_dict = relato_data.model_dump(exclude_unset=True)
    for key, value in relato_dict.items():
        setattr(db_relato, key, value)

    try:
        db.add(db_relato)
        db.commit()
        db.refresh(db_relato)
        return db_relato
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao atualizar o relato: {e}')


def delete_relato(db: Session, relato_id: int, user: Usuario) -> bool:
    """
    Deleta um relato.
    Apenas o proprietário do relato pode deletá-lo.
    """
    db_relato = db.get(Relato, relato_id)

    if not db_relato:
        return False  # Será tratado como 404 no controller

    # Regra de negócio: Apenas o usuário que criou o relato pode deletá-lo
    if db_relato.usuario_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Usuário não autorizado a deletar este relato")

    try:
        db.delete(db_relato)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao deletar o relato: {e}')


def get_latest_relatos(db: Session, offset: int, limit: int) -> Sequence[Relato]:
    """Busca os relatos mais recentes ordenados por data de registro."""
    relatos = db.exec(
        select(Relato)
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
        .order_by(Relato.data_furto.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return relatos

def get_my_relatos(db: Session, offset: int, limit: int, uid: int) -> Sequence[Relato]:
    """Busca relatos dos usuários apenas"""
    relatos = db.exec(
        select(Relato)
        .where(Relato.usuario_id == uid)
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
        .order_by(Relato.data_furto.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return relatos


def get_relatos_nearby(db: Session, latitude: float, longitude: float, radius_km: float) -> Sequence[Relato]:
    """
    Busca relatos próximos (filtrando em memória).
    NOTA: Isso é ineficiente para muitos dados. O ideal seria usar PostGIS (ST_DWithin),
    mas como 'haversine' já está no projeto, usei ele para filtrar em Python
    sem adicionar novas dependências de banco.
    """
    # Pega todos os relatos (ineficiente, mas funciona sem PostGIS)

    radius_em_metros = radius_km * 1000

    ponto_central_wkt = f'POINT({longitude} {latitude})'

    stmt = text(
        """
        SELECT id
        FROM relato
        WHERE ST_DWithin(
                      localizacao_geog,
                      ST_GeogFromText(:ponto_wkt),
                      :raio_metros
              )
        """
    )

    # Executa a consulta com segurança, passando os parâmetros
    params = {"ponto_wkt": ponto_central_wkt, "raio_metros": radius_em_metros}
    ids_dos_relatos = db.exec(stmt, params).scalars().all()

    if not ids_dos_relatos:
        return []

    # Etapa 2: Buscar os objetos Relato completos com suas fotos (eficiente)
    query = (
        select(Relato)
        .where(Relato.id.in_(ids_dos_relatos))
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
    )
    relatos = db.exec(query).all()

    return relatos


def create_relatos_batch(relatos_data: list[RelatoCreateDto], admin_user: Usuario, db: Session) -> int:
    """
    Cria múltiplos relatos em lote.
    Todos os relatos serão associados ao usuário admin que está fazendo o upload.
    Retorna a contagem de relatos criados.
    """
    count = 0
    try:
        for relato_dto in relatos_data:
            db_relato = Relato(**relato_dto.model_dump())
            db_relato.usuario_id = admin_user.id  # Associa ao admin
            db.add(db_relato)
            count += 1

        # Faz o commit de todos os novos relatos de uma vez
        db.commit()

        return count
    except Exception as e:
        db.rollback()
        # Se um falhar, nenhum é criado
        raise HTTPException(status_code=500, detail=f'Erro ao criar relatos em lote: {e}')


# 1. Obter relatos por Categoria
def get_relatos_by_category(db: Session, category_id: int, offset: int, limit: int) -> Sequence[Relato]:
    query = (
        select(Relato)
        .where(Relato.categoria_id == category_id)
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
        .offset(offset)
        .limit(limit)
    )
    return db.exec(query).all()

# 2. Obter relatos por Usuário Específico (Público)
def get_relatos_by_user_id(db: Session, user_id: int, offset: int, limit: int) -> Sequence[Relato]:
    query = (
        select(Relato)
        .where(Relato.usuario_id == user_id)
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
        .offset(offset)
        .limit(limit)
    )
    return db.exec(query).all()

# 3. Obter relatos por Intervalo de Datas
def get_relatos_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    offset: int,
    limit: int
) -> Sequence[Relato]:
    query = (
        select(Relato)
        .where(Relato.data_furto >= start_date)
        .where(Relato.data_furto <= end_date)
        .options(selectinload(Relato.fotos), selectinload(Relato.confirmacoes))
        .order_by(Relato.data_furto.desc())
        .offset(offset)
        .limit(limit)
    )
    return db.exec(query).all()