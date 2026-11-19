import os
import uuid

from fastapi import HTTPException, UploadFile, status

from ..schemas.upload import UploadRead
from ..storage.supabase_client import StorageNotConfigured, SupabaseStorage, storage

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# La extensión sale del tipo de contenido, nunca del nombre que manda el
# usuario (que puede mentir o traer rutas tipo "../../algo").
EXTENSIONES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
}


class StorageService:
    def __init__(self, backend: SupabaseStorage = storage):
        self.backend = backend

    def subir(self, archivo: UploadFile, usuario_id: int) -> UploadRead:
        content_type = (archivo.content_type or "").lower()
        extension = EXTENSIONES.get(content_type)
        if not extension:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Tipo de archivo no permitido. Usa JPG, PNG, WEBP o PDF",
            )

        # Se lee un byte de más para detectar archivos que pasan el límite
        # sin cargar en memoria un archivo enorme completo.
        contenido = archivo.file.read(MAX_UPLOAD_BYTES + 1)
        if not contenido:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo está vacío")
        if len(contenido) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo supera el máximo de {MAX_UPLOAD_MB} MB",
            )

        # El prefijo con el id del usuario es lo que permite luego saber
        # de quién es cada archivo (y verificarlo al borrar).
        file_name = f"{usuario_id}_{uuid.uuid4()}.{extension}"

        try:
            url = self.backend.upload(file_name, contenido, content_type)
        except StorageNotConfigured as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al subir el archivo a Supabase: {e}",
            )

        return UploadRead(file_name=file_name, url=url, content_type=content_type, size=len(contenido))

    def eliminar(self, file_name: str, usuario_id: int) -> None:
        # Solo nombres planos que empiecen con el id del usuario.
        if "/" in file_name or ".." in file_name or not file_name.startswith(f"{usuario_id}_"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

        try:
            self.backend.delete(file_name)
        except StorageNotConfigured as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al borrar el archivo en Supabase: {e}",
            )
