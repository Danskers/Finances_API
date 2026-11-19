from fastapi import Depends, FastAPI, File, UploadFile, status

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from .storage.upload_repository import obtener_upload
from .storage.upload_repository import inicializar_db
from .schemas.upload import UploadRead
from .security.jwt import get_current_usuario_id
from .services.storage_service import StorageService

app = FastAPI(title="Storage Service - Finanzas personales")

@app.on_event("startup")
def iniciar_base_datos():
    inicializar_db()

def get_service() -> StorageService:
    return StorageService()


@app.get("/health")
def health():
    return {"status": "ok", "service": "storage-service"}



@app.post("/uploads", status_code=status.HTTP_202_ACCEPTED)
def subir_archivo(
    archivo: UploadFile = File(...),
    usuario_id: int = Depends(get_current_usuario_id),
    service: StorageService = Depends(get_service),
):
    return service.iniciar_subida(archivo, usuario_id)

@app.delete("/uploads/{file_name}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_archivo(
    file_name: str,
    usuario_id: int = Depends(get_current_usuario_id),
    service: StorageService = Depends(get_service),
):
    service.eliminar(file_name, usuario_id)
    return None


@app.get("/uploads/{task_id}")
def consultar_upload(
    task_id: str,
    usuario_id: int = Depends(get_current_usuario_id),
):
    resultado = obtener_upload(task_id, usuario_id)

    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea de carga no encontrada",
        )

    return resultado