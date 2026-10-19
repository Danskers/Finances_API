import os
from typing import Optional

from supabase import Client, create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "facturas")


class StorageNotConfigured(Exception):
    """Supabase no está configurado o no se pudo conectar."""


class SupabaseStorage:
    """
    Envoltorio mínimo de Supabase Storage. Es el único archivo que conoce
    Supabase: si algún día se migra a S3, solo se reemplaza este archivo
    y se mantienen estos tres métodos.
    """

    def __init__(self) -> None:
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        # Cliente perezoso: se crea en el primer uso, no al arrancar, para
        # que el servicio levante aunque Supabase no esté configurado.
        if self._client is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise StorageNotConfigured("Faltan SUPABASE_URL o SUPABASE_KEY")
            try:
                self._client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                raise StorageNotConfigured(f"No se pudo conectar a Supabase: {e}")
        return self._client

    def upload(self, file_name: str, contents: bytes, content_type: str) -> str:
        bucket = self._get_client().storage.from_(SUPABASE_BUCKET)
        bucket.upload(file_name, contents, file_options={"content-type": content_type})
        return bucket.get_public_url(file_name)

    def delete(self, file_name: str) -> None:
        self._get_client().storage.from_(SUPABASE_BUCKET).remove([file_name])


storage = SupabaseStorage()
