from typing import List, Optional

from fastapi import Depends, FastAPI, Query, status
from sqlmodel import Session

from .database import crear_db, get_session
from .schemas.transaccion import (
    MES_REGEX,
    BalanceCuenta,
    LimiteRead,
    LimiteSet,
    ResumenMensual,
    TransaccionCreate,
    TransaccionRead,
)
from .security.jwt import CurrentUser, get_current_user
from .services.transaccion_service import TransaccionService

app = FastAPI(title="Transaction Service - Finanzas personales")


@app.on_event("startup")
def on_startup() -> None:
    crear_db()


def get_service(session: Session = Depends(get_session)) -> TransaccionService:
    return TransaccionService(session)


@app.get("/health")
def health():
    return {"status": "ok", "service": "transaction-service"}


# ---------- Transacciones ----------
@app.get("/transacciones", response_model=List[TransaccionRead])
def listar_transacciones(
    mes: Optional[str] = Query(default=None, pattern=MES_REGEX),
    q: Optional[str] = None,
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    return service.listar(user.usuario_id, mes, q)


@app.post("/transacciones", response_model=TransaccionRead, status_code=status.HTTP_201_CREATED)
def crear_transaccion(
    data: TransaccionCreate,
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    return service.crear(data, user.usuario_id, user.token)


@app.delete("/transacciones/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(
    tx_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    service.eliminar(tx_id, user.usuario_id)
    return None


# ---------- Límite mensual ----------
@app.put("/limites", response_model=LimiteRead)
def fijar_limite(
    data: LimiteSet,
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    return service.fijar_limite(data, user.usuario_id)


@app.get("/limites/{mes}", response_model=LimiteRead)
def obtener_limite(
    mes: str,
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    return service.obtener_limite(user.usuario_id, mes)


# ---------- Dashboard / historial ----------
@app.get("/resumen", response_model=ResumenMensual)
def resumen_mensual(
    mes: Optional[str] = Query(default=None, pattern=MES_REGEX),
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    return service.resumen(user.usuario_id, mes)


@app.get("/balances", response_model=List[BalanceCuenta])
def balances_por_cuenta(
    user: CurrentUser = Depends(get_current_user),
    service: TransaccionService = Depends(get_service),
):
    return service.balances(user.usuario_id)
