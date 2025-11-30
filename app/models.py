from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

    cuentas: List["Cuenta"] = Relationship(back_populates="usuario")
    transacciones: List["Transaccion"] = Relationship(back_populates="usuario")
    limites: List["LimiteMensual"] = Relationship(back_populates="usuario")

class Cuenta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    usuario_id: int = Field(foreign_key="usuario.id")

    usuario: Usuario = Relationship(back_populates="cuentas")
    transacciones: List["Transaccion"] = Relationship(back_populates="cuenta")

class Transaccion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    tipo: str  # ingreso / gasto / deuda
    categoria: str  # fijo / variable
    subcategoria: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.utcnow)
    mes: str = Field(default="")  # 'YYYY-MM'

    usuario_id: int = Field(foreign_key="usuario.id")
    cuenta_id: int = Field(foreign_key="cuenta.id")

     #URL a la imagen subida a Supabase
    factura_url: Optional[str] = None

    usuario: Usuario = Relationship(back_populates="transacciones")
    cuenta: Cuenta = Relationship(back_populates="transacciones")


class LimiteMensual(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    mes: str  # 'YYYY-MM'
    monto_limite: float = 0.0

    usuario: Usuario = Relationship(back_populates="limites")
