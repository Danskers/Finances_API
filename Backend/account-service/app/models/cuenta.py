from typing import Optional

from sqlmodel import Field, SQLModel


class Cuenta(SQLModel, table=True):
    __tablename__ = "cuenta"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

    usuario_id: int = Field(index=True)
