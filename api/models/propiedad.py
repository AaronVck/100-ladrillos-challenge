from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class Property(BaseModel):
    id: int
    nombre_propiedad: str
    nombre_empresa: str
    dueno_propiedad: int
    ladrillos_maximos: int
    ladrillos_actuales: int
    ladrillos_restantes: int

