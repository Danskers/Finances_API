from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from ..models.cuenta import Cuenta
from ..repositories.cuenta_repository import CuentaRepository
from ..schemas.cuenta import CuentaCreate, CuentaUpdate


class CuentaService:
    def __init__(self, session: Session):
        self.repo = CuentaRepository(session)

    def listar(self, usuario_id: int) -> List[Cuenta]:
        return self.repo.list_by_usuario(usuario_id)

    def obtener(self, cuenta_id: int, usuario_id: int) -> Cuenta:
        cuenta = self.repo.get_by_id(cuenta_id)
        self._verificar_pertenencia(cuenta, usuario_id)
        return cuenta

    def crear(self, data: CuentaCreate, usuario_id: int) -> Cuenta:
        nueva = Cuenta(nombre=data.nombre, usuario_id=usuario_id)
        return self.repo.create(nueva)

    def actualizar(self, cuenta_id: int, data: CuentaUpdate, usuario_id: int) -> Cuenta:
        cuenta = self.repo.get_by_id(cuenta_id)
        self._verificar_pertenencia(cuenta, usuario_id)
        cuenta.nombre = data.nombre
        return self.repo.update(cuenta)

    def eliminar(self, cuenta_id: int, usuario_id: int) -> None:
        cuenta = self.repo.get_by_id(cuenta_id)
        self._verificar_pertenencia(cuenta, usuario_id)

        if self.repo.tiene_transacciones(cuenta_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una cuenta con transacciones",
            )

        self.repo.delete(cuenta)

    def _verificar_pertenencia(self, cuenta: Optional[Cuenta], usuario_id: int) -> None:
        if not cuenta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
        if cuenta.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta cuenta")
