from fastapi import Depends, FastAPI, File, UploadFile, status

from .schemas.upload import UploadRead
from .security.jwt import get_current_usuario_id
from .services.storage_service import StorageService

app = FastAPI(title="Storage Service - Finanzas personales")


def get_service() -> StorageService:
    return StorageService()


@app.get("/health")
def health():
    return {"status": "ok", "service": "storage-service"}



@app.post("/uploads", response_model=UploadRead, status_code=status.HTTP_201_CREATED)
def subir_archivo(
    archivo: UploadFile = File(...),
    usuario_id: int = Depends(get_current_usuario_id),
    service: StorageService = Depends(get_service),
):
    return service.subir(archivo, usuario_id)


@app.delete("/uploads/{file_name}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_archivo(
    file_name: str,
    usuario_id: int = Depends(get_current_usuario_id),
    service: StorageService = Depends(get_service),
):
    service.eliminar(file_name, usuario_id)
    return None
