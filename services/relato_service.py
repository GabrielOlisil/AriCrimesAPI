from typing import Sequence

from fastapi import HTTPException, status

from dtos import RelatoCreateDto
from sqlmodel import Session, select, text
from models import Relato, Usuario


def create_relato(relato: RelatoCreateDto, user: Usuario,  db: Session):

    try:
        db_relato = Relato(**relato.model_dump())

        db_relato.usuario_id = user.id

        db.add(db_relato)
        db.commit()
        db.refresh(db_relato)
        return db_relato
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao criar o relato {e}')


def get_all_relatos(db: Session, offset: int, limit: int) -> Sequence[Relato]:
        relatos = db.exec(select(Relato).offset(offset).limit(limit)).all()
        return relatos


def get_relato_by_id(db: Session, relato_id: int) -> Relato | None:
    """Busca um relato específico pelo ID."""
    relato = db.get(Relato, relato_id)
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
        .order_by(Relato.data_registro.desc())
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
        SELECT *
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

    # Executamos a consulta SQL nativa e mapeamos os resultados de volta
    # para a classe (modelo) Pydantic/SQLModel 'Relato'.
    resultados = db.exec(stmt, params).all()

    # Converte os resultados (que são Tuples/Rows) de volta para objetos Relato
    # Se db.exec(stmt).all() já retornar objetos Relato, melhor ainda.
    # Mas se retornar Rows, precisamos mapear:
    relatos_proximos = [Relato.model_validate(row, from_attributes=True) for row in resultados]

    return relatos_proximos


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