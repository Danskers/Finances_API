from typing import List, Optional

from sqlalchemy import text
from sqlmodel import Session, select

from ..models.cuenta import Cuenta


class CuentaRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, cuenta_id: int) -> Optional[Cuenta]:
        return self.session.get(Cuenta, cuenta_id)

    def list_by_usuario(self, usuario_id: int) -> List[Cuenta]:
        statement = select(Cuenta).where(Cuenta.usuario_id == usuario_id)
        return self.session.exec(statement).all()

    def create(self, cuenta: Cuenta) -> Cuenta:
        self.session.add(cuenta)
        self.session.commit()
        self.session.refresh(cuenta)
        return cuenta

    def update(self, cuenta: Cuenta) -> Cuenta:
        self.session.add(cuenta)
        self.session.commit()
        self.session.refresh(cuenta)
        return cuenta

    def delete(self, cuenta: Cuenta) -> None:
        self.session.delete(cuenta)
        self.session.commit()

    def tiene_transacciones(self, cuenta_id: int) -> bool:
        """
        Puente temporal mientras transaction-service no está separado:
        la tabla "transaccion" vive en la misma BD compartida, así que se
        consulta con SQL crudo (sin importar el modelo Transaccion, que
        no le pertenece a este servicio) para no acoplar el código entre
        servicios.

        Cuando transaction-service tenga su propia BD y API, esto debe
        reemplazarse por una llamada HTTP, ej.:
            GET http://transaction-service/transacciones/existe?cuenta_id=...
        """
        result = self.session.execute(
            text("SELECT COUNT(*) FROM transaccion WHERE cuenta_id = :cid"),
            {"cid": cuenta_id},
        )
        count = result.scalar() or 0
        return count > 0
