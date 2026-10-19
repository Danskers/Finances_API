from fastapi import Depends, FastAPI, status
from sqlmodel import Session

from .database import crear_db, get_session
from .schemas.usuario import TokenResponse, UsuarioCreate, UsuarioLogin, UsuarioRead
from .services.auth_service import AuthService

app = FastAPI(title="Auth Service - Finanzas personales")


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
