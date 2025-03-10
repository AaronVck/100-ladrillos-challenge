from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class BuyerBricks(BaseModel):
    id_compra: int
    id_comprador_vendedor: int
    id_propiedad: int
    cantidad_ladrillos: int
    enProceso_y_comprado: Optional[int] = 0



