import os

import httpx
from fastapi import HTTPException, status
from sqlmodel import Session

from ..models.usuario import Usuario
from ..repositories.usuario_repository import UsuarioRepository
from ..schemas.usuario import UsuarioCreate, UsuarioLogin
from ..security.jwt import crear_token
from ..security.password import get_password_hash, verify_password

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8001")


class AuthService:
    def __init__(self, session: Session):
        self.repo = UsuarioRepository(session)

    def registrar(self, data: UsuarioCreate) -> Usuario:
        existente = self.repo.get_by_email(data.email)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado",
            )

        hashed = get_password_hash(data.password)
        nuevo = Usuario(email=data.email, hashed_password=hashed)
        nuevo = self.repo.create(nuevo)

        self._crear_cuenta_principal(nuevo.id)

        return nuevo

    def login(self, data: UsuarioLogin) -> str:
        usuario = self.repo.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        return crear_token({"sub": str(usuario.id)})

    def _crear_cuenta_principal(self, usuario_id: int) -> None:
        """
        Llamada HTTP real a account-service para crear la cuenta por
        defecto, como hacía el monolito directo en la BD.

        A propósito NO lanza una excepción si account-service está caído
        o tarda demasiado: el registro del usuario ya se completó y no
        debe fallar por un problema de OTRO servicio. Si falla, el
        usuario simplemente puede crear su cuenta manualmente después.
        Esto es "degradación elegante" (graceful degradation).
        """
        token_interno = crear_token({"sub": str(usuario_id)})
        try:
            with httpx.Client(timeout=5.0) as client:
                client.post(
                    f"{ACCOUNT_SERVICE_URL}/cuentas",
                    json={"nombre": "Cuenta principal"},
                    headers={"Authorization": f"Bearer {token_interno}"},
                )
        except httpx.RequestError as e:
            print(f"⚠️  No se pudo crear la cuenta principal automáticamente: {e}")
