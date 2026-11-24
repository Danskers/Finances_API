
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


def validar_fortaleza(password: str) -> str:
    """Reglas de contraseña compartidas por el registro y la edición de perfil."""
    if not any(caracter.isdigit() for caracter in password):
        raise ValueError("La contraseña debe contener al menos un número")

    if not any(caracter.isalpha() for caracter in password):
        raise ValueError("La contraseña debe contener al menos una letra")

    if not any(
        not caracter.isalnum() and not caracter.isspace()
        for caracter in password
    ):
        raise ValueError("La contraseña debe contener al menos un símbolo")

    return password


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def validar_password(cls, password: str):
        return validar_fortaleza(password)


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioUpdate(BaseModel):
    """Edición del perfil. Siempre exige la contraseña actual."""

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
    password_actual: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, password: Optional[str]):
        return validar_fortaleza(password) if password is not None else None


class UsuarioRead(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
