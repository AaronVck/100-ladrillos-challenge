from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from api.services.usuario import UserService
from api.models.usuario import User
from api.db.connection import database
from api.utils.seguridad import get_password_hash, verify_password, create_access_token

router = APIRouter()


def get_user_service() -> UserService:
    return UserService(database)


@router.post("/registrar")
async def create_user(user: User, db: UserService = Depends(get_user_service)):
    """Registra un nuevo usuario en la base de datos."""
    # Verificar si el usuario ya existe
    existing_user = await db.get_user(user.nombre)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya registrado")

    await db.create_user(user)

    return JSONResponse(status_code=200, content={"message": "Usuario registrado exitosamente"})

@router.post("/iniciarSesion")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: UserService = Depends(get_user_service)):
    """Verifica las credenciales y genera un token JWT si son correctas."""
    user_bd = await db.get_user(form_data.username, form_data.password)
    if not user_bd or not verify_password(form_data.password, user_bd["contrasena"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Generar el token con la información del usuario
    access_token = create_access_token(data={"sub": user_bd["nombre"], "id": user_bd["id"]})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/usuarios")
async def get_users(db: UserService = Depends(get_user_service)):
    try:
        users = await db.get_users()
        if not users:
            return JSONResponse(content={[]}, status_code=200)

        return JSONResponse(content=users, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo los usuarios: {str(e)}")


@router.patch("/{user_id}", response_model=bool)
async def update_user(nombre: Optional[str] = Form(""),
                      contrasena: Optional[str] = Form(""),
                      user_id: int | None = None,
                      db: UserService = Depends(get_user_service)):
    try:
        updated = await db.update_user(nombre, contrasena, user_id)
        return JSONResponse(content={"updated": updated}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando el usuario: {str(e)}")


@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: int, db: UserService = Depends(get_user_service)):
    try:
        deleted = await db.delete_user(user_id)
        return JSONResponse(content={"deleted": deleted}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando el usuario: {str(e)}")


