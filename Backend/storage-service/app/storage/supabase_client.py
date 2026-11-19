
import os
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client


# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "facturas")


class StorageNotConfigured(Exception):
    """Supabase no está configurado o ocurrió un error en Storage."""


class SupabaseStorage:

    def __init__(self) -> None:
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        """
        Crea el cliente de Supabase cuando se necesita por primera vez.
        """

        if self._client is None:

            if not SUPABASE_URL or not SUPABASE_KEY:
                raise StorageNotConfigured(
                    "Faltan SUPABASE_URL o SUPABASE_KEY"
                )

            try:
                self._client = create_client(
                    SUPABASE_URL,
                    SUPABASE_KEY
                )

            except Exception as e:
                raise StorageNotConfigured(
                    f"No se pudo crear el cliente de Supabase: {e}"
                ) from e

        return self._client

    def upload(
        self,
        file_name: str,
        contents: bytes,
        content_type: str
    ) -> str:
        """
        Sube un archivo al bucket de Supabase Storage.
        Retorna la URL pública del archivo.
        """

        try:
            bucket = self._get_client().storage.from_(
                SUPABASE_BUCKET
            )

            bucket.upload(
                file_name,
                contents,
                file_options={
                    "content-type": content_type
                }
            )

            return bucket.get_public_url(file_name)

        except Exception as e:
            raise StorageNotConfigured(
                f"Error al subir archivo a Supabase: {e}"
            ) from e

    def delete(self, file_name: str) -> None:
        """
        Elimina un archivo del bucket de Supabase Storage.
        """

        try:
            bucket = self._get_client().storage.from_(
                SUPABASE_BUCKET
            )

            bucket.remove([file_name])

        except Exception as e:
            raise StorageNotConfigured(
                f"Error al eliminar archivo de Supabase: {e}"
            ) from e


# Instancia reutilizable del servicio
storage = SupabaseStorage()