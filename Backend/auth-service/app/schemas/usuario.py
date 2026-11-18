
from pydantic import BaseModel, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def validar_password(cls, password: str):
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


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioRead(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
