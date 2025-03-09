from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class BuyerBricks(BaseModel):
    id_comprador_vendedor: int
    id_propiedad: int
    cantidad_ladrillos: int
    alta_baja: Optional[int] = 1



