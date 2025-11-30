from fastapi import APIRouter, UploadFile, File, HTTPException
from supabase import Client
from datetime import datetime
import uuid

from app.main import supabase

router = APIRouter()

@router.post("/upload-factura")
async def upload_factura(file: UploadFile = File(...)):
    # Validar tipo
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Formato no permitido. Solo JPG y PNG.")

    # Nombre único
    unique_name = f"{uuid.uuid4()}-{file.filename}"

    try:
        # Leemos el archivo
        file_data = await file.read()

        # Subir al bucket
        supabase.storage.from_("facturas").upload(
            path=unique_name,
            file=file_data,
            file_options={"content-type": file.content_type}
        )

        # Crear URL pública
        public_url = supabase.storage.from_("facturas").get_public_url(unique_name)

        return {
            "message": "Factura subida exitosamente",
            "file_url": public_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
