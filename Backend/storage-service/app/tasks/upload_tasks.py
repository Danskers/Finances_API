
import logging
from pathlib import Path

from app.celery_app import celery_app
from app.storage.supabase_client import storage
from app.storage.upload_repository import actualizar_upload

logger = logging.getLogger(__name__)

TEMP_DIR = Path("/app/temp_uploads")


@celery_app.task
def procesar_upload(task_id, file_path, file_name, content_type):

    ruta = Path(file_path).resolve()

    try:
        # Verificar que el archivo esté dentro del directorio temporal.
        if not ruta.is_relative_to(TEMP_DIR.resolve()):
            raise ValueError("Ruta de archivo no permitida")

        # Marcar la tarea como procesando.
        actualizar_upload(task_id, "processing")

        # Leer el archivo temporal.
        contenido = ruta.read_bytes()

        # Subir la factura a Supabase.
        url = storage.upload(
            file_name,
            contenido,
            content_type
        )

        # Guardar el resultado.
        actualizar_upload(
            task_id,
            "completed",
            url=url
        )

        return {
            "task_id": task_id,
            "status": "completed",
            "url": url
        }

    except Exception:
        logger.exception("Error procesando la factura %s", task_id)

        actualizar_upload(
            task_id,
            "failed",
            error="No fue posible procesar la factura"
        )

        raise

    finally:
        # Eliminar el archivo temporal.
        ruta.unlink(missing_ok=True)
