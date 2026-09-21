import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# Durante la migración gradual, account-service sigue apuntando al mismo
# archivo SQLite que usaba el monolito. Cuando se separe la BD, esto pasa
# a ser una URL propia (ej. postgresql://.../account_db) vía variable de
# entorno, sin tocar el resto del código.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finanzas1.sqlite3")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def crear_db() -> None:
    """
    Crea únicamente las tablas que este servicio conoce (Cuenta).
    No toca las tablas de usuario, transaccion ni limite_mensual: esas
    las crean auth-service y transaction-service. Como por ahora
    comparten el mismo archivo SQLite, esto es seguro: create_all()
    no borra ni sobreescribe tablas que ya existen.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
