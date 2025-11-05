from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from database import SessionDep
from models import Usuario
from dtos import FotoRelatoResponseDto

from services.auth_service import get_current_user
import services.foto_relato_service as foto_relato_service
import services.storage_service as storage_service

router = APIRouter(prefix="/relato", tags=["Fotos de Relatos"])


@router.post(
    "/{relato_id}/foto/",
    response_model=FotoRelatoResponseDto,
    status_code=status.HTTP_201_CREATED
)
async def upload_foto_para_relato(
        relato_id: int,
        db: SessionDep,
        user: Usuario = Depends(get_current_user),
        file: UploadFile = File(..., description="Arquivo de imagem para upload (jpg, png, etc.)")
):
    """
    **Sumário:** Adicionar Foto a um Relato (via Proxy).

    **Descrição:** Recebe um ficheiro de imagem, o encaminha para o
    servidor de ficheiros e associa a URL retornada a um relato existente.

    **Regra de Negócio:** O usuário autenticado deve ser o **proprietário** do relato para poder adicionar uma foto.

    **Resposta:** O objeto da foto (com ID, URL pública e relato_id).
    """

    # 1. Verificar se o relato existe e se o utilizador é o dono
    try:
        db_relato = foto_relato_service.check_relato_ownership(
            db=db,
            relato_id=relato_id,
            user_id=user.id
        )
    except HTTPException as e:
        raise e  # Repassa o erro (403 ou 404)

    # 2. Enviar o ficheiro para o file-server (Node)
    try:
        public_url = storage_service.proxy_file_to_storage(file=file)
    except HTTPException as e:
        raise e  # Repassa o erro (400, 503, 500, etc.)

    # 3. Salvar a URL pública no banco de dados
    try:
        db_foto = foto_relato_service.create_foto_relato_db(
            db=db,
            url=public_url,
            relato=db_relato  # Passamos o relato que já buscámos
        )

        return FotoRelatoResponseDto(
            id=db_foto.id,
            url=db_foto.url,
            relato_id=db_foto.relato_id
        )
    except HTTPException as e:
        # TODO: Se o DB falhar, a foto ficou "órfã" no file-server.
        # Uma implementação futura pode chamar uma rota de DELETE no file-server.
        raise e