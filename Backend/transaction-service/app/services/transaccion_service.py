from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from ..clients.account_client import AccountClient
from ..models.transaccion import LimiteMensual, Transaccion
from ..repositories.transaccion_repository import TransaccionRepository
from ..schemas.transaccion import (
    BalanceCuenta,
    LimiteSet,
    ResumenMensual,
    TransaccionCreate,
)


def mes_actual() -> str:
    return datetime.utcnow().strftime("%Y-%m")


class TransaccionService:
    def __init__(self, session: Session, account_client: Optional[AccountClient] = None):
        self.repo = TransaccionRepository(session)
        self.accounts = account_client or AccountClient()

    # ---------- Transacciones ----------
    def listar(self, usuario_id: int, mes: Optional[str] = None, q: Optional[str] = None) -> List[Transaccion]:
        trans = self.repo.list_by_usuario_mes(usuario_id, mes or mes_actual())

        if q:
            ql = q.lower()
            trans = [
                t for t in trans
                if ql in t.categoria.lower()
                or (t.subcategoria and ql in t.subcategoria.lower())
                or ql in t.tipo.lower()
                or ql in str(t.monto)
                or ql in t.fecha.strftime("%Y-%m-%d")
            ]
        return trans

    def crear(self, data: TransaccionCreate, usuario_id: int, token: str) -> Transaccion:
        # Valida con account-service que la cuenta existe y es del usuario.
        self.accounts.verificar_cuenta(data.cuenta_id, token)

        nueva = Transaccion(
            monto=data.monto,
            tipo=data.tipo,
            categoria=data.categoria,
            subcategoria=data.subcategoria,
            cuenta_id=data.cuenta_id,
            usuario_id=usuario_id,
            mes=mes_actual(),
            factura_url=data.factura_url,
        )
        return self.repo.create(nueva)

    def eliminar(self, tx_id: int, usuario_id: int) -> None:
        tx = self.repo.get_by_id(tx_id)
        if not tx or tx.usuario_id != usuario_id:
            # Mismo 404 en ambos casos para no revelar que el id existe.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        self.repo.delete(tx)

    # ---------- Límite mensual ----------
    def fijar_limite(self, data: LimiteSet, usuario_id: int) -> LimiteMensual:
        existente = self.repo.get_limite(usuario_id, data.mes)
        if existente:
            existente.monto_limite = data.monto_limite
            return self.repo.save_limite(existente)
        return self.repo.save_limite(
            LimiteMensual(usuario_id=usuario_id, mes=data.mes, monto_limite=data.monto_limite)
        )

    def obtener_limite(self, usuario_id: int, mes: str) -> LimiteMensual:
        limite = self.repo.get_limite(usuario_id, mes)
        return limite or LimiteMensual(usuario_id=usuario_id, mes=mes, monto_limite=0.0)

    # ---------- Resúmenes (dashboard / historial) ----------
    def resumen(self, usuario_id: int, mes: Optional[str] = None) -> ResumenMensual:
        mes_q = mes or mes_actual()
        trans = self.repo.list_by_usuario_mes(usuario_id, mes_q)

        total_ingresos = sum(t.monto for t in trans if t.tipo == "ingreso")
        total_gastos = sum(t.monto for t in trans if t.tipo in ("gasto", "deuda"))
        monto_limite = self.obtener_limite(usuario_id, mes_q).monto_limite

        return ResumenMensual(
            mes=mes_q,
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            monto_limite=monto_limite,
            disponible=monto_limite - total_gastos,
        )

    def balances(self, usuario_id: int) -> List[BalanceCuenta]:
        return [
            BalanceCuenta(cuenta_id=cid, balance=bal)
            for cid, bal in sorted(self.repo.balances_por_cuenta(usuario_id).items())
        ]
