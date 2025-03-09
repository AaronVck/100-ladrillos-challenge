from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from starlette import status
from api.services.usuario import UserService
from api.models.usuario import User
from api.db.connection import database
from api.utils.seguridad import get_password_hash

router = APIRouter()


def get_user_service() -> UserService:
    return UserService(database)


@router.post("/registrar")
async def create_user(user: User, db: UserService = Depends(get_user_service)):
    """Registra un nuevo usuario en la base de datos."""
    # Verificar si el usuario ya existe
    existing_user = await db.get_user(user)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya registrado")

    await db.create_user(user)

    return JSONResponse(status_code=200, content={"message": "Usuario registrado exitosamente"})


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