from api.db.connection import Database
from typing import Optional
from api.utils.seguridad import get_password_hash, verify_password
from api.models.propiedad import Property
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PropertyService:
    def __init__(self, db: Database):
        self.db = db

    async def create_property(self, data_property: Property, id_dueno: int) -> int:
        query = ("INSERT INTO property (nombre_propiedad, nombre_empresa, dueno_propiedad, ladrillos_maximos, "
                 "ladrillos_actuales, ladrillos_restantes, valor_del_ladrillo) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (data_property.nombre_propiedad, data_property.nombre_empresa,
                                           id_dueno, data_property.ladrillos_maximos,
                                           data_property.ladrillos_maximos, data_property.ladrillos_maximos,
                                           data_property.valor_del_ladrillo))
                await conn.connection.commit()
                return conn.lastrowid
        except Exception as e:
            await conn.connection.rollback()
            raise e

    async def get_all_properties(self) -> Optional[dict]:
        query = ("SELECT property.id, user.nombre AS dueno_propiedad, property.nombre_propiedad, property.nombre_empresa, "
                 "property.ladrillos_maximos,"
                 "property.ladrillos_restantes, property.valor_del_ladrillo FROM user INNER JOIN property ON user.id "
                 "= property.dueno_propiedad WHERE property.alta_baja = 1")
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query)
                return await conn.fetchall()
        except Exception as err:
            return {"Error": err}

    async def get_property(self, id_property: int) -> Optional[dict]:
        query = ("SELECT property.id, user.nombre AS dueno_propiedad, user.id AS dueno_id, property.nombre_propiedad, property.nombre_empresa, "
                 "property.ladrillos_maximos,"
                 "property.ladrillos_restantes, property.valor_del_ladrillo FROM user INNER JOIN property ON user.id "
                 "= property.dueno_propiedad WHERE property.alta_baja = 1 AND property.id = %s")
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, id_property)
                return await conn.fetchone()
        except Exception as e:
            await conn.connection.rollback()
            raise e

    async def update_property(self, valor_ladrillos: float | None =  None,
                              ladrillos_maximos: int | None =  None,
                              nombre_propiedad: str | None =  None,
                              id: int | None =  None) -> bool:
        base_query = "UPDATE property SET"
        final_query = "WHERE id = %s"
        condition = []
        values = []
        if valor_ladrillos != 0.0 and valor_ladrillos is not None:
            condition.append("valor_del_ladrillo = %s")
            values.append(valor_ladrillos)
        if ladrillos_maximos != 0 and ladrillos_maximos is not None:
            condition.append("ladrillos_maximos = %s, ladrillos_restantes = %s")
            values.append(ladrillos_maximos)
            values.append(ladrillos_maximos)
        if nombre_propiedad != '' and nombre_propiedad is not None:
            condition.append("nombre_propiedad = %s")
            values.append(nombre_propiedad)

        values.append(id)

        final_condition = ", ".join(condition)
        final_query = f"{str(base_query)} {str(final_condition)} {str(final_query)}"

        async for conn in self.db.get_connection():
            try:
                await conn.connection.begin()
                await conn.execute(final_query, (tuple(values)))
                await conn.connection.commit()
                return True
            except Exception as e:
                await conn.connection.rollback()
                raise e

    async def delete_property(self, id: int) -> bool:
        query = "UPDATE property SET alta_baja = 0 WHERE id = %s"
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (id,))
                await conn.connection.commit()
                return conn.rowcount > 0
        except Exception as e:
            await conn.connection.rollback()
            raise e