from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    nombre: str
    contasena: str
