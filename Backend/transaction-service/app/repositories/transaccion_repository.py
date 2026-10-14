from typing import Dict, List, Optional

from sqlmodel import Session, select

from ..models.transaccion import LimiteMensual, Transaccion


class TransaccionRepository:
    def __init__(self, session: Session):
        self.session = session

    # ---------- Transacciones ----------
    def list_by_usuario_mes(self, usuario_id: int, mes: str) -> List[Transaccion]:
        statement = (
            select(Transaccion)
            .where(Transaccion.usuario_id == usuario_id)
            .where(Transaccion.mes == mes)
            .order_by(Transaccion.fecha.desc())
        )
        return self.session.exec(statement).all()

    def list_by_usuario(self, usuario_id: int) -> List[Transaccion]:
        statement = select(Transaccion).where(Transaccion.usuario_id == usuario_id)
        return self.session.exec(statement).all()

    def get_by_id(self, tx_id: int) -> Optional[Transaccion]:
        return self.session.get(Transaccion, tx_id)

    def create(self, tx: Transaccion) -> Transaccion:
        self.session.add(tx)
        self.session.commit()
        self.session.refresh(tx)
        return tx

    def delete(self, tx: Transaccion) -> None:
        self.session.delete(tx)
        self.session.commit()

    def balances_por_cuenta(self, usuario_id: int) -> Dict[int, float]:
        balances: Dict[int, float] = {}
        for t in self.list_by_usuario(usuario_id):
            delta = t.monto if t.tipo == "ingreso" else -t.monto
            balances[t.cuenta_id] = balances.get(t.cuenta_id, 0.0) + delta
        return balances

    # ---------- Límite mensual ----------
    def get_limite(self, usuario_id: int, mes: str) -> Optional[LimiteMensual]:
        statement = (
            select(LimiteMensual)
            .where(LimiteMensual.usuario_id == usuario_id)
            .where(LimiteMensual.mes == mes)
        )
        return self.session.exec(statement).first()

    def save_limite(self, limite: LimiteMensual) -> LimiteMensual:
        self.session.add(limite)
        self.session.commit()
        self.session.refresh(limite)
        return limite
