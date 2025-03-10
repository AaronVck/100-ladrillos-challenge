from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from api.utils.seguridad import get_current_user
from api.models.compradorLadrillos import BuyerBricks
from api.services.compradorLadrillos import BuyService
from api.services.propiedad import PropertyService
from api.db.connection import database

def get_property_service() -> PropertyService:
    return PropertyService(database)

def get_buy_service() -> BuyService:
    return BuyService(database)


router = APIRouter()


@router.post("/agregarAlCarrito")
async def add_to_cart(id_propiedad: int = Form(), cantidad_ladrillos: int = Form(),
                      current_user: dict = Depends(get_current_user), db: BuyService = Depends(get_buy_service),
                      db_properties: PropertyService = Depends(get_property_service)):

    if current_user:
        propiedad = await db_properties.get_property(id_propiedad)
        if propiedad:
            if propiedad['dueno_id'] == current_user['id']:
                raise HTTPException(status_code=500, detail=f"Error, no puedes comprar ladrillos de tu propia propiedad")
            # propiedad['ladrillos_maximos'] < cantidad_ladrillos (Pertenecia abajo, lo usaré para la ultima validacion)
            if (propiedad['ladrillos_restantes'] - cantidad_ladrillos) < 0:
                raise HTTPException(status_code=500,
                                    detail=f"Error, la cantidad de ladrillos que deseas comprar excede los ladrillos maximos disponibles")

            pre_compra = await db.pre_buy_bricks(current_user['id'],
                                         propiedad['id'],
                                         cantidad_ladrillos,
                                         (propiedad['ladrillos_restantes'] - cantidad_ladrillos))
            if pre_compra:
                return JSONResponse(content="Su compra esta en el carrito, confirmela", status_code=200)

        else:
            raise HTTPException(status_code=500, detail={"Error": "Sucedio un error al crear la propiedad, verifique sus datos"})
    else:
        raise HTTPException(status_code=500, detail={"Error": "Inicie sesión para agregar una compra al carrito"})


@router.get("/obtenerComprasPendientes")
async def get_compras_en_carrito(current_user: dict = Depends(get_current_user), db: BuyService = Depends(get_buy_service),
                      db_properties: PropertyService = Depends(get_property_service)):
    if current_user:
        result = await db.get_all_detalles(current_user['id'])
        try:
            if result:
                return JSONResponse(content=result, status_code=200)
        except Exception as err:
            raise HTTPException(status_code=500,
                                    detail=f"Error al obtener los status de compra - {err}")
    else:
        raise {"Error": "Inicie sesión para confirmar una compra"}

@router.get("/obtenerCompraFactura")
async def get_compra_en_carrito(current_user: dict = Depends(get_current_user),
                                 id_detalles: int | None = None,
                                 db: BuyService = Depends(get_buy_service),):
    if current_user:
        result = await db.get_one_detalles(current_user['id'], id_detalles)
        try:
            if result:
                return JSONResponse(content=result, status_code=200)
        except Exception as err:
            raise HTTPException(status_code=500,
                                    detail=f"Error al obtener el status de compra - {err}")
    else:
        raise {"Error": "Inicie sesión para confirmar una compra"}

@router.get("/obtenerFacturas")
async def get_compras_en_carrito(current_user: dict = Depends(get_current_user),
                                 db: BuyService = Depends(get_buy_service),):
    if current_user:
        result = await db.get_all_facturas(current_user['id'])
        try:
            if result:
                return JSONResponse(content=result, status_code=200)
        except Exception as err:
            raise HTTPException(status_code=500,
                                    detail=f"Error al obtener los status de compra - {err}")
    else:
        raise {"Error": "Inicie sesión para confirmar una compra"}

@router.post("/confirmarCompra")
async def confirmar_compra(id_compra: int = Form(),
                           confirmar_compra: bool = Form(..., description="Acepto los terminos y servicios"),
                           current_user: dict = Depends(get_current_user), db: BuyService = Depends(get_buy_service),
                           db_properties: PropertyService = Depends(get_property_service)):
    if not confirmar_compra:
        raise HTTPException(status_code=500, detail=f"Debe confirmar nuestros terminos y servicios para comprar ladrillos")
    if current_user:
        detalles = await db.get_one_detalles(current_user['id'], id_compra)
        if detalles:
            if detalles['enproceso_y_comprado'] == 1:
                raise HTTPException(status_code=500, detail=f"Este pedido ya se ha realizado, busque otros pedidos pendientes")
            propiedad = await db_properties.get_property(detalles['propiedad_id'])
            if propiedad:
                if propiedad['ladrillos_restantes'] < detalles['Ladrillos_A_Comprar']:
                    raise HTTPException(status_code=500,
                                        detail=f"Error, la cantidad de ladrillos que desea comprar no se encuentra disponible")
                if (propiedad['ladrillos_restantes'] - detalles['Ladrillos_A_Comprar']) < 0:

                    raise HTTPException(status_code=500, detail=f"Error, la cantidad de ladrillos que desea comprar excede la cantidad disponible")
                try:
                    if detalles['usuario_id'] == current_user['id']:
                        result = await db.definitive_buy_bricks(id_compra,
                                                 propiedad['ladrillos_restantes'] - detalles['Ladrillos_A_Comprar'],
                                                 detalles['propiedad_id'])
                        if result == 1:
                            return JSONResponse(content="Su compra se ha confirmado con exito")
                except Exception as err:
                    raise HTTPException(status_code=500, detail=f"Sucedió un error al confirmar la compra - {err}")

        else:
            raise HTTPException(status_code=500, detail={"Error": "Sucedio un error al crear la propiedad, verifique sus datos"})
    else:
        raise HTTPException(status_code=500, detail={"Error": "Inicie sesión para agregar una compra al carrito"})


@router.patch("/{id_compra}")
async def update_pedido(id_compra: int, cantidad_ladrillos: int = Form(None),
                        current_user: dict = Depends(get_current_user),
                        db: BuyService = Depends(get_buy_service)):
    if current_user:
        try:
            result = await db.update_pedido(id_compra, cantidad_ladrillos)
            if result:
                return JSONResponse(content="La actualizacion se hizo con exito", status_code=200)
            raise HTTPException(status_code=500, detail={"Error": "Ocurrio un error al actualizar el pedido"})
        except Exception as err:
            raise HTTPException(status_code=500, detail={"Error": f"Ocurrio un erro - {err}"})
    raise HTTPException(status_code=500, detail={"Error": "Inicie sesión para actualizar un pedido"})


@router.post("/venderLadrillos")
async def sell_ladrillos(id_factura: int, ladrillos_devueltos: int, current_user: dict = Depends(get_current_user),
                         db: BuyService = Depends(get_buy_service)):
    if current_user:
        factura = await db.get_one_detalles(current_user['id'], id_factura)
        try:
            if factura:
                if ladrillos_devueltos > factura['Ladrillos_A_Comprar']:
                    raise HTTPException(status_code=500,
                                detail=f"Error, debe devolver una cantidad menor a los ladrillos que tiene en posesion")
                regreso = await db.sell_bricks(id_factura, ladrillos_devueltos, factura['propiedad_id'])
                if regreso:
                    return JSONResponse(content="Los ladrillos se han devuelto con exito", status_code=200)
                pass
        except Exception as err:
            raise HTTPException(status_code=500,
                                detail=f"Error al obtener los status de compra - {err}")
