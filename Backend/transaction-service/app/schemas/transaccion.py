from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

MES_REGEX = r"^\d{4}-(0[1-9]|1[0-2])$"


class TransaccionCreate(BaseModel):
    monto: float = Field(..., gt=0)
    tipo: Literal["ingreso", "gasto", "deuda"]
    categoria: str = Field(..., min_length=1, max_length=100)
    subcategoria: Optional[str] = Field(default=None, max_length=100)
    cuenta_id: int
    # La URL viene de storage-service, que es quien sube el archivo.
    factura_url: Optional[str] = None


class TransaccionRead(BaseModel):
    id: int
    monto: float
    tipo: str
    categoria: str
    subcategoria: Optional[str]
    fecha: datetime
    mes: str
    usuario_id: int
    cuenta_id: int
    factura_url: Optional[str]

    class Config:
        from_attributes = True


class LimiteSet(BaseModel):
    mes: str = Field(..., pattern=MES_REGEX)
    monto_limite: float = Field(..., ge=0)


class LimiteRead(BaseModel):
    mes: str
    monto_limite: float

    class Config:
        from_attributes = True


class ResumenMensual(BaseModel):
    mes: str
    total_ingresos: float
    total_gastos: float
    monto_limite: float
    disponible: float


class BalanceCuenta(BaseModel):
    cuenta_id: int
    balance: float
