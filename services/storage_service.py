import os
import requests
from fastapi import UploadFile, HTTPException, status
from requests.exceptions import RequestException

# Carrega a configuração do ambiente
FILE_SERVER_UPLOAD_URL = os.getenv("FILE_SERVER_UPLOAD_URL")
FILE_SERVER_SECRET = os.getenv("FILE_SERVER_SECRET")

if not FILE_SERVER_UPLOAD_URL or not FILE_SERVER_SECRET:
    raise ValueError("FILE_SERVER_UPLOAD_URL e FILE_SERVER_SECRET devem ser definidos.")


def proxy_file_to_storage(file: UploadFile) -> str:
    """
    Encaminha (proxy) um UploadFile para o serviço de ficheiros interno,
    autenticando-se com um header secreto.

    Retorna a URL pública final que o serviço de ficheiros nos devolveu.
    """

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo inválido. Apenas imagens são permitidas."
        )

    headers = {
        "x-upload-secret": FILE_SERVER_SECRET
    }

    # Prepara o ficheiro para ser "repassado"
    files_to_upload = {
        'file': (file.filename, file.file, file.content_type)
    }

    try:
        # Faz o pedido para o seu file-server (Node)
        response = requests.post(
            FILE_SERVER_UPLOAD_URL,
            headers=headers,
            files=files_to_upload
        )

        response.raise_for_status()  # Lança exceção para erros (401, 403, 500)

        response_data = response.json()

        # O seu serviço Node DEVE retornar um JSON como: {"url": "https://..."}
        if "url" not in response_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Serviço de ficheiros não retornou uma URL válida."
            )

        return response_data["url"]

    except RequestException as e:
        print(f"Erro de rede ao contactar file-server: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Não foi possível conectar ao serviço de ficheiros."
        )
    except Exception as e:
        print(f"Erro ao encaminhar ficheiro: {e}")
        if hasattr(e, 'response') and e.response is not None:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro do serviço de ficheiros: {e.response.text}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro desconhecido no upload."
        )
    finally:
        file.file.close()