from fastapi import FastAPI,APIRouter
from api.db.connection import Database
from api.controllers.CompraVenta import router as compra_venta_router
from api.controllers.Usuarios import router as usuarios_router
from api.controllers.Propiedades import router as propiedades_router
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

# Database
DATABASE_CONFIG = {
    "host": os.getenv('DB_HOST'),
    "port": int(os.getenv('DB_PORT')),
    "user": os.getenv('DB_USER'),
    "password":  os.getenv('DB_PASS'),
    "db": os.getenv('DB_NAME')
}

database = Database(**DATABASE_CONFIG)
router = APIRouter()

async def lifespan(app: FastAPI):
    await database.connect()
    print("DB conectada")
    yield  #aplicacion incia aqui
    await database.disconnect()
    print("DB Desconectada")

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
)

@router.get("/")
async def main():
    response_data = {
        "Status": "Funcional?"
        }
    return JSONResponse(content=response_data, status_code=200)

app.include_router(router)
# Publico
app.include_router(usuarios_router, prefix="/usuarios", tags=["100LadrillosCreacionUsuarios"])
# Protegidos
app.include_router(compra_venta_router, prefix="/compraVenta", tags=["100LadrillosCompraVenta"])
app.include_router(propiedades_router, prefix="/propiedades", tags=["100LadrillosPropiedades"])
