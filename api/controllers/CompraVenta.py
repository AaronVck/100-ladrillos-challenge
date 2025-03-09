from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from api.utils.seguridad import get_current_user

router = APIRouter()


@router.get("/test_endpoint")
async def obtain_data(current_user: dict = Depends(get_current_user)):
    return JSONResponse(content=[{"Prueba": f"Bien - Hola {current_user['nombre']}"}], status_code=200)