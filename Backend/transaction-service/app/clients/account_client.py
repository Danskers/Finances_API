import os

import httpx
from fastapi import HTTPException, status

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8001")


class AccountClient:
    """Cliente HTTP de account-service."""

    def verificar_cuenta(self, cuenta_id: int, token: str) -> None:
        """
        Confirma que la cuenta existe y pertenece al usuario del token.

        Si account-service está caído se RECHAZA la operación (503). A
        diferencia del registro de usuarios, aquí no se degrada: guardar
        una transacción en una cuenta no verificada dejaría datos
        inconsistentes que luego no se pueden distinguir de los buenos.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    f"{ACCOUNT_SERVICE_URL}/cuentas/{cuenta_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo verificar la cuenta: account-service no responde",
            )

        if resp.status_code == 200:
            return
        if resp.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
        if resp.status_code == 403:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta cuenta")
        if resp.status_code == 401:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token rechazado por account-service")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Respuesta inesperada de account-service ({resp.status_code})",
        )
