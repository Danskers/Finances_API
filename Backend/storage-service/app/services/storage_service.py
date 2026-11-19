
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from ..storage.upload_repository import (
    crear_upload,
    actualizar_upload,
)
from ..tasks.upload_tasks import procesar_upload


MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

TEMP_DIR = Path("/app/temp_uploads")

EXTENSIONES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
}


class StorageService:

    def iniciar_subida(self, archivo: UploadFile, usuario_id: int):

        content_type = (archivo.content_type or "").lower()
        extension = EXTENSIONES.get(content_type)

        if not extension:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Tipo de archivo no permitido. Usa JPG, PNG, WEBP o PDF",
            )

        contenido = archivo.file.read(MAX_UPLOAD_BYTES + 1)

        if not contenido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío",
            )

        if len(contenido) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo supera el máximo de {MAX_UPLOAD_MB} MB",
            )

        task_id = str(uuid.uuid4())
        file_name = f"{usuario_id}_{uuid.uuid4()}.{extension}"

        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        file_path = TEMP_DIR / f"{task_id}.{extension}"

        registro_creado = False

        try:
            # Guardar el archivo temporalmente.
            file_path.write_bytes(contenido)

            # Registrar la tarea en SQLite.
            crear_upload(
                task_id,
                usuario_id,
                file_name,
                content_type,
                len(contenido),
            )

            registro_creado = True

            # Enviar la tarea a Celery mediante RabbitMQ.
            procesar_upload.apply_async(
                args=[
                    task_id,
                    str(file_path),
                    file_name,
                    content_type,
                ],
                task_id=task_id,
            )

            # Responder sin esperar a que Supabase termine.
            return {
                "task_id": task_id,
                "status": "pending",
                "file_name": file_name,
            }

        except Exception as e:

            # Eliminar el archivo temporal si ocurre un error.
            file_path.unlink(missing_ok=True)

            # Evitar que el registro quede pendiente si falla el envío.
            if registro_creado:
                try:
                    actualizar_upload(
                        task_id,
                        "failed",
                        error="No fue posible enviar la tarea a procesamiento",
                    )
                except Exception:
                    pass

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No fue posible iniciar el procesamiento de la factura",
            ) from e


    def eliminar(self, file_name: str, usuario_id: int) -> None:

        if (
            "/" in file_name
            or "\\" in file_name
            or ".." in file_name
            or not file_name.startswith(f"{usuario_id}_")
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado",
            )

        from ..storage.supabase_client import (
            StorageNotConfigured,
            storage,
        )

        try:
            storage.delete(file_name)

        except StorageNotConfigured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo acceder a Supabase Storage",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error al eliminar el archivo",
            )
