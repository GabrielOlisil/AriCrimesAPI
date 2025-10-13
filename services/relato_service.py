from typing import Sequence

from fastapi import HTTPException

from dtos import RelatoCreateDto
from sqlmodel import Session, select
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
        raise HTTPException(status_code=500, detail=f'Erro ao criar o relato {e}')


def get_all_relatos(db: Session, offset: int, limit: int) -> Sequence[Relato]:
        relatos = db.exec(select(Relato).offset(offset).limit(limit)).all()
        return relatos