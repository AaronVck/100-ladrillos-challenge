from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class Property(BaseModel):
    id: Optional[int]
    nombre_propiedad: str
    nombre_empresa: str
    dueno_propiedad: int
    ladrillos_maximos: int
    ladrillos_actuales: int
    ladrillos_restantes: int
    valor_del_ladrillo: float
    alta_baja: Optional[int] = 1

