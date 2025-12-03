from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Nombre de tu archivo SQLite
DATABASE_NAME = "finanzas1.sqlite3"

# URL usando ese nombre
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # Requerido para SQLite en FastAPI
)

def crear_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
