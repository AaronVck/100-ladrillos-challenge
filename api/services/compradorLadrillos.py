from api.db.connection import Database
from typing import Optional
from api.utils.seguridad import get_password_hash, verify_password
from api.models.compradorLadrillos import BuyerBricks
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BuyService:
    def __init__(self, db: Database):
        self.db = db

    async def pre_buy_bricks(self, id_comprador_vendedor: int, id_propiedad: int, cantidad_ladrillos: int, ladrillos_restantes: int) -> int:
        query_join = ("INSERT INTO shopping (id_comprador_vendedor, id_propiedad, cantidad_ladrillos) "
                 "VALUES (%s, %s, %s)")
        # query_propiedad = ("UPDATE property SET ladrillos_restantes = %s WHERE id = %s")
        async for conn in self.db.get_connection():
            try:
                await conn.connection.begin()
                # await conn.execute(query_propiedad, (ladrillos_restantes, id_propiedad))
                await conn.execute(query_join, (id_comprador_vendedor, id_propiedad, cantidad_ladrillos))
                await conn.connection.commit()
                return 1
            except Exception as e:
                await conn.connection.rollback()
                raise e

    async def definitive_buy_bricks(self, id_compra: int, ladrillos_restantes: int, id_propiedad: int):
        query_property = "UPDATE property SET ladrillos_restantes = %s WHERE id = %s"
        query_shopping = "UPDATE shopping SET enproceso_y_comprado = 1 WHERE id_compra = %s"
        async for conn in self.db.get_connection():
            try:
                await conn.connection.begin()
                await conn.execute(query_property, (ladrillos_restantes, id_propiedad))
                await conn.execute(query_shopping, id_compra)
                await conn.connection.commit()
                return 1
            except Exception as e:
                await conn.connection.rollback()
                raise e

    async def get_all_detalles(self, id_comprador_vendedor: int) -> Optional[dict]:
        query = ("SELECT "
                 "shopping.id_compra AS Identificador_De_Compra,"
                 "user.nombre AS Comprador,"
                 "property.nombre_propiedad,"
                 "property.nombre_empresa,"
                 "shopping.cantidad_ladrillos as Ladrillos_A_Comprar,"
                 "property.valor_del_ladrillo,"
                 "(shopping.cantidad_ladrillos * property.valor_del_ladrillo) AS Total_A_Pagar,"
                 "shopping.enproceso_y_comprado "
                 "FROM shopping "
                 "INNER JOIN user ON shopping.id_comprador_vendedor = user.id "
                 "INNER JOIN property ON shopping.id_propiedad = property.id WHERE shopping.id_comprador_vendedor = %s "
                 "AND shopping.enproceso_y_comprado = 0;")
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (id_comprador_vendedor))
                return await conn.fetchall()
        except Exception as err:
            return {"Error": err}

    async def get_one_detalles(self, id_comprador_vendedor: int, id_detalles: int) -> Optional[dict]:
        query = ("SELECT "
                 "shopping.id_compra AS Identificador_De_Compra,"
                 "user.nombre AS Comprador,"
                 "user.id AS usuario_id,"
                 "property.nombre_propiedad,"
                 "property.nombre_empresa,"
                 "property.id as propiedad_id,"
                 "shopping.cantidad_ladrillos as Ladrillos_A_Comprar,"
                 "property.valor_del_ladrillo,"
                 "(shopping.cantidad_ladrillos * property.valor_del_ladrillo) AS Total_A_Pagar,"
                 "shopping.enproceso_y_comprado "
                 "FROM shopping "
                 "INNER JOIN user ON shopping.id_comprador_vendedor = user.id "
                 "INNER JOIN property ON shopping.id_propiedad = property.id WHERE shopping.id_comprador_vendedor = %s "
                 "AND shopping.id_compra = %s")
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (id_comprador_vendedor, id_detalles))
                return await conn.fetchone()
        except Exception as err:
            return {"Error": err}

    async def update_pedido(self, id_pedido, cantidad_ladrillos: int) -> bool:
        query = "UPDATE shopping SET cantidad_ladrillos = %s WHERE id_compra = %s"

        async for conn in self.db.get_connection():
            try:
                await conn.execute(query, (cantidad_ladrillos, id_pedido))
                await conn.connection.commit()
                return True
            except Exception as e:
                await conn.connection.rollback()
                raise e

    async def get_all_facturas(self, id_comprador_vendedor: int):
        query = ("SELECT "
                 "shopping.id_compra AS Identificador_De_Compra,"
                 "user.nombre AS Comprador,"
                 "property.nombre_propiedad,"
                 "property.nombre_empresa,"
                 "shopping.cantidad_ladrillos as Ladrillos_Comprados,"
                 "property.valor_del_ladrillo,"
                 "(shopping.cantidad_ladrillos * property.valor_del_ladrillo) AS Total_Pagado,"
                 "shopping.enproceso_y_comprado "
                 "FROM shopping "
                 "INNER JOIN user ON shopping.id_comprador_vendedor = user.id "
                 "INNER JOIN property ON shopping.id_propiedad = property.id WHERE shopping.id_comprador_vendedor = %s "
                 "AND shopping.enproceso_y_comprado = 1;")
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (id_comprador_vendedor))
                return await conn.fetchall()
        except Exception as err:
            return {"Error": err}

    async def sell_bricks(self, id_compra: int, ladrillos_a_devolver: int, id_propiedad: int):
        query_property = "UPDATE property SET ladrillos_restantes = ladrillos_restantes + %s WHERE id = %s"
        query_shopping = "UPDATE shopping SET cantidad_ladrillos = cantidad_ladrillos - %s WHERE id_compra = %s"
        async for conn in self.db.get_connection():
            try:
                await conn.connection.begin()
                await conn.execute(query_property, (ladrillos_a_devolver, id_propiedad))
                await conn.execute(query_shopping, (ladrillos_a_devolver, id_compra))
                await conn.connection.commit()
                return 1
            except Exception as e:
                await conn.connection.rollback()
                raise e


