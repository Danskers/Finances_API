import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# Mismo archivo SQLite compartido que el monolito mientras dura la migración.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finanzas1.sqlite3")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def crear_db() -> None:
    """Crea las tablas de este servicio (transaccion y limitemensual) si no existen."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
