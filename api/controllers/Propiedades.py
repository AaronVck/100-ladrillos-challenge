from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from api.models.propiedad import Property
from api.utils.seguridad import get_current_user
from api.services.propiedad import PropertyService
from api.db.connection import database


def get_property_service() -> PropertyService:
    return PropertyService(database)


router = APIRouter()


@router.post("/crearPropiedad")
async def create_property(property: Property, current_user: dict = Depends(get_current_user),
                          db: PropertyService = Depends(get_property_service)):
    if current_user:
        result = await db.create_property(property, current_user['id'])
        if result:

            return JSONResponse(content=[{"message": "Propiedad creada con exito"}], status_code=200)
        else:
            raise {"Error": "Sucedio un error al crear la propiedad, verifique sus datos"}
    else:
        raise {"Error": "Inicie sesión para crear una propiedad"}

@router.get("/verPropiedades")
async def get_all_properties(current_user: dict = Depends(get_current_user),
                             db: PropertyService = Depends(get_property_service)):
    results = await db.get_all_properties()
    if results:
        try:
            return JSONResponse(content=results, status_code=200)
        except Exception as err:
            raise {"Error": f"Sucedió un error al obtener las propiedades - {err}"}
    else:
        raise {"Error": "Sucedió un error al obtener las propiedades"}

@router.get("/verPropiedad/{id_property}")
async def get_property(id_property: int, current_user: dict = Depends(get_current_user),
                             db: PropertyService = Depends(get_property_service)):
    try:
        result = await db.get_property(id_property)
        if result:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=500, detail=f"Error Obteniendo la propiedad")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo la propiedad: {str(e)}")

@router.patch("/{id_property}")
async def update_property_owner(id_property: int, valor_ladrillos: Optional[float] = Form(None), ladrillos_maximos: Optional[int] =Form(None),
                                nombre_propiedad: Optional[str] = Form(None), current_user: dict = Depends(get_current_user),
                                db: PropertyService = Depends(get_property_service)):
    try:
        result = await db.get_property(id_property)
        if result:
            if result['dueno_id'] == current_user['id']:
                if result['ladrillos_maximos'] == result['ladrillos_restantes'] and (ladrillos_maximos != 0 or valor_ladrillos != 0.0):
                    if ladrillos_maximos != 0 or valor_ladrillos != 0.0:
                        result = await db.update_property(valor_ladrillos, ladrillos_maximos, nombre_propiedad, current_user['id'])
                        if result:
                            return JSONResponse(content="La actualizacion se hizo con exito", status_code=200)

                    else:
                        raise HTTPException(status_code=500,
                                            detail=f"Para modificar la propiedad no debe tener ladrillos vendidos")
                elif nombre_propiedad != 'string':
                    result = await db.update_property(valor_ladrillos, ladrillos_maximos, nombre_propiedad,
                                                      current_user['id'])
                    if result:
                        return JSONResponse(content="La actualizacion se hizo con exito", status_code=200)
                else:
                    raise HTTPException(status_code=500, detail=f"Para modificar la propiedad agregue parametros correctos")
            else:
                raise HTTPException(status_code=500, detail=f"No eres el dueno de esta propiedad")
        else:
            raise HTTPException(status_code=500, detail=f"Error Obteniendo la propiedad")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo la propiedad: {str(e)}")


@router.delete("/{id_property}")
async def update_property_owner(id_property: int, current_user: dict = Depends(get_current_user),
                                db: PropertyService = Depends(get_property_service)):
    try:
        result = await db.get_property(id_property)
        if result:
            if result['dueno_id'] == current_user['id']:
                try:
                    deleted = await db.delete_property(id_property)
                    return JSONResponse(content={"deleted": deleted}, status_code=200)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error eliminando la propiedad: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"No eres el dueno de esta propiedad")
        else:
            raise HTTPException(status_code=500, detail=f"Error Obteniendo la propiedad")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Eliminando la propiedad: {str(e)}")
