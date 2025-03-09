from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/test_endpoint")
async def obtain_data():
    return JSONResponse(content=[{"Prueba": "Bien"}], status_code=200)