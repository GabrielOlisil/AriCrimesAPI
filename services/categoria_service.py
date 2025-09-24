
from dtos import CategoriaCreateDto
from sqlmodel import Session, select
from models import Categoria

def create_categoria(categoria: CategoriaCreateDto, db: Session):
    db_categoria = Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


def get_all_categorias(db: Session, offset: int, limit: int) -> list[Categoria]:
    categorias = db.exec(select(Categoria).offset(offset).limit(limit)).all()
    return categorias

def try_update_categorias(db: Session, categoria: CategoriaCreateDto, id: int) -> None | Categoria:
    db_categoria = db.get(Categoria, id)
    if db_categoria is None:
        return None

    db_categoria.nome = categoria.nome
    db_categoria.descricao = categoria.descricao
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def try_delete_categoria(db: Session, id: int) -> bool:
    db_categoria = db.get(Categoria, id)
    if db_categoria is None:
        return False

    db.delete(db_categoria)
    db.commit()

    return True