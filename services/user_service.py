from sqlmodel import Session, select

from models import Categoria, Usuario


def get_all_users(db: Session, offset: int, limit: int) -> list[Usuario]:
    return db.exec(select(Usuario).offset(offset).limit(limit)).all()


def try_update_users(db: Session, categoria: CategoriaCreateDto, id: int) -> None | Categoria:
    db_categoria = db.get(Categoria, id)
    if db_categoria is None:
        return None

    db_categoria.nome = categoria.nome
    db_categoria.descricao = categoria.descricao
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def try_delete_users(db: Session, id: int) -> bool:
    db_categoria = db.get(Categoria, id)
    if db_categoria is None:
        return False

    db.delete(db_categoria)
    db.commit()

    return True