import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

# Debe ser EXACTAMENTE el mismo SECRET_KEY que usan los demás servicios
# (account-service, el futuro transaction-service, etc.) para validar
# los tokens que este servicio emite.
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_TO_A_VERY_SECURE_RANDOM_KEY_PLEASE")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
