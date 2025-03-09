from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    nombre: str
    contrasena: str
    alta_baja: Optional[int] = 1
