import os

import httpx
from fastapi import HTTPException, status
from sqlmodel import Session

from ..models.usuario import Usuario
from ..repositories.usuario_repository import UsuarioRepository
from ..schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioUpdate
from ..security.jwt import crear_token
from ..security.password import get_password_hash, verify_password

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8001")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8003")


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

    def obtener_perfil(self, usuario_id: int) -> Usuario:
        usuario = self.repo.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
        )

        return usuario

    def actualizar_perfil(self, usuario_id: int, data: UsuarioUpdate) -> Usuario:
        """Cambia el correo y/o la contraseña. Exige la contraseña actual."""
        usuario = self.obtener_perfil(usuario_id)

        if not verify_password(data.password_actual, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La contraseña actual es incorrecta",
            )

        if data.email is None and data.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay cambios para guardar",
            )

        if data.email is not None and data.email != usuario.email:
            if self.repo.get_by_email(data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ese correo ya está en uso",
                )
            usuario.email = data.email

        if data.password is not None:
            usuario.hashed_password = get_password_hash(data.password)

        return self.repo.update(usuario)

    def eliminar_perfil(self, usuario_id: int) -> None:
        """
        Borra al usuario. Antes limpia sus datos en los otros servicios
        (transacciones y cuentas) para que no queden huérfanos: SQLite puede
        reutilizar el id de un usuario borrado y el siguiente en registrarse
        vería datos ajenos.
        """
        usuario = self.obtener_perfil(usuario_id)
        self._borrar_datos_del_usuario(usuario_id)
        self.repo.delete(usuario)

    def _borrar_datos_del_usuario(self, usuario_id: int) -> None:
        token = crear_token({"sub": str(usuario_id)})
        headers = {"Authorization": f"Bearer {token}"}
        try:
            with httpx.Client(timeout=5.0, headers=headers) as client:
                transacciones = client.get(f"{TRANSACTION_SERVICE_URL}/transacciones")
                if transacciones.status_code == 200:
                    for tx in transacciones.json():
                        client.delete(f"{TRANSACTION_SERVICE_URL}/transacciones/{tx['id']}")
                cuentas = client.get(f"{ACCOUNT_SERVICE_URL}/cuentas")
                if cuentas.status_code == 200:
                    for cuenta in cuentas.json():
                        client.delete(f"{ACCOUNT_SERVICE_URL}/cuentas/{cuenta['id']}")
        except httpx.RequestError as e:
            # Como en el registro: otro servicio caído no debe impedir borrar el perfil.
            print(f"⚠️  No se pudieron limpiar los datos del usuario {usuario_id}: {e}")

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
