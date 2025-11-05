from sqlmodel import Session
from models import FotoRelato, Relato
from fastapi import HTTPException, status


def check_relato_ownership(db: Session, relato_id: int, user_id: int) -> Relato:
    """
    Verifica se um relato existe e se o utilizador é o dono.
    Retorna o objeto Relato se for bem-sucedido, ou lança exceção.
    """
    db_relato = db.get(Relato, relato_id)
    if not db_relato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relato não encontrado."
        )

    if db_relato.usuario_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não autorizado a adicionar fotos a este relato."
        )

    return db_relato


def create_foto_relato_db(db: Session, url: str, relato: Relato) -> FotoRelato:
    """
    Salva a referência da URL da foto no banco de dados.
    Assume que a verificação de propriedade já foi feita.
    """
    try:
        # Usa o __tablename__ 'fotorelato'
        db_foto = FotoRelato(url=url, relato_id=relato.id)
        db.add(db_foto)
        db.commit()
        db.refresh(db_foto)
        return db_foto
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar referência da foto no banco de dados: {e}"
        )