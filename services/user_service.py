from sqlmodel import Session, select

from models import Categoria, Usuario


def get_all_users(db: Session, offset: int, limit: int) -> list[Usuario]:
    return db.exec(select(Usuario).offset(offset).limit(limit)).all()

