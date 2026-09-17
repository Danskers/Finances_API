from typing import List

from fastapi import Depends, FastAPI, status
from sqlmodel import Session

from .database import crear_db, get_session
from .schemas.cuenta import CuentaCreate, CuentaRead, CuentaUpdate
from .security.jwt import get_current_usuario_id
from .services.cuenta_service import CuentaService

app = FastAPI(title="Account Service - Finanzas personales")


@app.on_event("startup")
def on_startup() -> None:
    crear_db()


def get_cuenta_service(session: Session = Depends(get_session)) -> CuentaService:
    return CuentaService(session)


@app.get("/health")
def health():
    return {"status": "ok", "service": "account-service"}


@app.get("/cuentas", response_model=List[CuentaRead])
def listar_cuentas(
    usuario_id: int = Depends(get_current_usuario_id),
    service: CuentaService = Depends(get_cuenta_service),
):
    return service.listar(usuario_id)


@app.get("/cuentas/{cuenta_id}", response_model=CuentaRead)
def obtener_cuenta(
    cuenta_id: int,
    usuario_id: int = Depends(get_current_usuario_id),
    service: CuentaService = Depends(get_cuenta_service),
):
    return service.obtener(cuenta_id, usuario_id)


@app.post("/cuentas", response_model=CuentaRead, status_code=status.HTTP_201_CREATED)
def crear_cuenta(
    data: CuentaCreate,
    usuario_id: int = Depends(get_current_usuario_id),
    service: CuentaService = Depends(get_cuenta_service),
):
    return service.crear(data, usuario_id)


@app.put("/cuentas/{cuenta_id}", response_model=CuentaRead)
def actualizar_cuenta(
    cuenta_id: int,
    data: CuentaUpdate,
    usuario_id: int = Depends(get_current_usuario_id),
    service: CuentaService = Depends(get_cuenta_service),
):
    return service.actualizar(cuenta_id, data, usuario_id)


@app.delete("/cuentas/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta(
    cuenta_id: int,
    usuario_id: int = Depends(get_current_usuario_id),
    service: CuentaService = Depends(get_cuenta_service),
):
    service.eliminar(cuenta_id, usuario_id)
    return None
