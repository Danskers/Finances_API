from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Transaccion(SQLModel, table=True):
    __tablename__ = "transaccion"

    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    tipo: str  # ingreso / gasto / deuda
    categoria: str
    subcategoria: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.utcnow)
    mes: str = Field(default="", index=True)  # 'YYYY-MM'

    # En el monolito estas dos eran foreign_key a usuario.id y cuenta.id.
    # Esas tablas pertenecen a auth-service y account-service, así que aquí
    # son enteros simples. La existencia de la cuenta se valida llamando a
    # account-service por HTTP (ver clients/account_client.py).
    usuario_id: int = Field(index=True)
    cuenta_id: int = Field(index=True)

    # Solo guardamos la URL. La subida del archivo es de storage-service.
    factura_url: Optional[str] = None


class LimiteMensual(SQLModel, table=True):
    __tablename__ = "limitemensual"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(index=True)
    mes: str  # 'YYYY-MM'
    monto_limite: float = 0.0
