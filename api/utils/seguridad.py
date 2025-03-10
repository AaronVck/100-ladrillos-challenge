from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()

# Clave secreta para firmar los tokens (debería estar en variables de entorno)
SECRET_KEY = os.getenv('TOKEN_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Contexto para encriptar y verificar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 para obtener tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/iniciarSesion", scopes={})


def get_password_hash(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        return {"nombre": username, "id": user_id}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")



