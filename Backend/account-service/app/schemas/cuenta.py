from pydantic import BaseModel, Field


class CuentaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class CuentaUpdate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class CuentaRead(BaseModel):
    id: int
    nombre: str
    usuario_id: int

    class Config:
        from_attributes = True  # permite construir el schema desde el modelo SQLModel
