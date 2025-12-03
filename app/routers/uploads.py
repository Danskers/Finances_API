from fastapi import APIRouter, UploadFile, File, HTTPException, Request  # ← Agregamos Request
from supabase import Client
from datetime import datetime
import uuid

router = APIRouter(prefix="/uploads", tags=["uploads"])  # Opcional: buen prefijo


@router.post("/upload-factura")
async def upload_factura(request: Request, file: UploadFile = File(...)):  # ← Agregamos request
    # Validar tipo
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Formato no permitido. Solo JPG, PNG y PDF.")

    # Nombre único
    unique_name = f"{uuid.uuid4()}-{file.filename}"

    try:
        # Leemos el archivo
        file_data = await file.read()

        # Accedemos al cliente de Supabase desde app.state
        supabase_client: Client = request.app.state.supabase

        # Subir al bucket "facturas"
        supabase_client.storage.from_("facturas").upload(
            path=unique_name,
            file=file_data,
            file_options={"content-type": file.content_type}
        )

        # Crear URL pública
        public_url = supabase_client.storage.from_("facturas").get_public_url(unique_name)

        return {
            "message": "Factura subida exitosamente",
            "file_url": public_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la factura: {str(e)}")
