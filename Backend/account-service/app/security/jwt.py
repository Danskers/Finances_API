import os
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

# Debe ser exactamente el mismo SECRET_KEY y ALGORITHM que usa auth-service
# para firmar los tokens (compártelo vía variable de entorno / secret,
# nunca lo dupliques a mano en cada servicio).
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_TO_A_VERY_SECURE_RANDOM_KEY_PLEASE")
ALGORITHM = "HS256"


def _get_token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return request.cookies.get("access_token")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_usuario_id(request: Request) -> int:
    """
    Dependency de FastAPI que reemplaza a get_user_from_request del monolito.

    A propósito NO consulta la tabla "usuario": esa tabla pertenece a
    auth-service y account-service no debe acoplarse a su esquema. Basta
    con confiar en el JWT ya firmado por auth-service y leer el "sub".
    """
    token = _get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    try:
        return int(sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
