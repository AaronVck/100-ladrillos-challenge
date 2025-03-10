from api.db.connection import Database
from typing import Optional
from api.utils.seguridad import get_password_hash, verify_password
from api.models.usuario import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def create_user(self, data_user: User) -> int:
        query = "INSERT INTO user (nombre, contrasena) VALUES (%s, %s)"
        hashed_password = get_password_hash(data_user.contrasena)
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (data_user.nombre, hashed_password))
                await conn.connection.commit()
                return conn.lastrowid
        except Exception as e:
            await conn.connection.rollback()
            raise e

    async def get_user(self, nombre: Optional[str] | None = None, contrasena: Optional[str] | None = None, id: Optional[int] | None = None) -> Optional[dict]:
        if nombre:
            query = "SELECT id, contrasena, nombre, alta_baja FROM user WHERE nombre = %s AND alta_baja = 1"
            values = [nombre]
        elif id:
            query = "SELECT id, nombre, alta_baja FROM user WHERE id = %s AND alta_baja = 1"
            values = [id]
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, tuple(values))
                return await conn.fetchone()
        except Exception as err:
            return {"Error": err}

    async def get_users(self) -> list:
        query = "SELECT id, nombre, alta_baja FROM user WHERE alta_baja = 1"
        async for conn in self.db.get_connection():
            await conn.execute(query)
            return await conn.fetchall()

    async def update_user(self, nombre: str, contrasena: str, id: int) -> bool:

        if contrasena != '':
            hashed_password = get_password_hash(contrasena)
            if verify_password(contrasena, hashed_password):

                query = "UPDATE user SET contrasena = %s WHERE id = %s"
                params = (hashed_password, id)
            else:
                raise ["Contrasena Incorrecta"]
        elif nombre != '':
            query = "UPDATE user SET nombre = %s WHERE id = %s"
            params = (nombre, id)
        elif contrasena != '' and nombre != '':
            hashed_password = get_password_hash(contrasena)
            query = "UPDATE user SET nombre = %s, contrasena = %s WHERE id = %s"
            params = (hashed_password, id)
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, params)
                await conn.connection.commit()
                return conn.rowcount > 0
        except Exception as e:
            await conn.connection.rollback()
            raise e

    async def delete_user(self, id: int) -> bool:
        query = "UPDATE user SET alta_baja = 0 WHERE id = %s"
        try:
            async for conn in self.db.get_connection():
                await conn.execute(query, (id,))
                await conn.connection.commit()
                return conn.rowcount > 0
        except Exception as e:
            await conn.connection.rollback()
            raise e
