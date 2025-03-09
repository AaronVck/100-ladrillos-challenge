import aiomysql
from dotenv import load_dotenv
import os

load_dotenv()
class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str = os.getenv('DB_HOST'),
                 port: int = int(os.getenv('DB_PORT')),
                 user: str = os.getenv('DB_USER'),
                 password: str = os.getenv('DB_PASS'),
                 db: str = os.getenv('DB_NAME')):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._db = db
        self._pool = None

    async def connect(self):
        self._pool = await aiomysql.create_pool(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db=self._db,
            minsize=1,
            maxsize=100,
        )

    async def disconnect(self):
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

    async def get_connection(self):
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                yield cursor

# Global singleton
database = Database()