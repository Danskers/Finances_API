from fastapi import Depends, FastAPI, status
from sqlmodel import Session

from .database import crear_db, get_session
from .schemas.usuario import (
    TokenResponse,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioRead,
    UsuarioUpdate,
)
from .services.auth_service import AuthService
from .security.jwt import get_current_usuario_id

app = FastAPI(
    title="Auth Service - Finanzas personales",
    root_path="/auth"
)


@app.on_event("startup")
def on_startup() -> None:
    crear_db()


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}


@app.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def register(data: UsuarioCreate, service: AuthService = Depends(get_auth_service)):
    return service.registrar(data)


@app.post("/login", response_model=TokenResponse)
def login(data: UsuarioLogin, service: AuthService = Depends(get_auth_service)):
    token = service.login(data)
    return TokenResponse(access_token=token)

@app.get("/me", response_model=UsuarioRead)
def obtener_perfil(
    usuario_id: int = Depends(get_current_usuario_id),
    service: AuthService = Depends(get_auth_service),
):
    return service.obtener_perfil(usuario_id)


@app.put("/me", response_model=UsuarioRead)
def actualizar_perfil(
    data: UsuarioUpdate,
    usuario_id: int = Depends(get_current_usuario_id),
    service: AuthService = Depends(get_auth_service),
):
    return service.actualizar_perfil(usuario_id, data)


@app.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_perfil(
    usuario_id: int = Depends(get_current_usuario_id),
    service: AuthService = Depends(get_auth_service),
):
    service.eliminar_perfil(usuario_id)
