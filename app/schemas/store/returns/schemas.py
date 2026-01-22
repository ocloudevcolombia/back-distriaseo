from pydantic import BaseModel
from typing import Optional
from app.schemas.store.customers.schemas import CustomerOut
from datetime import datetime

class ReturnBase(BaseModel):
    amount_returned: float  # Cambiamos 'debt' por 'amount_returned'

class ReturnCreate(ReturnBase):
    pass

class ReturnUpdate(BaseModel):
    amount_returned: Optional[float] = None  # El campo es ahora opcional para actualizaciones

    class Config:
        from_attributes = True

class ReturnOut(ReturnBase):
    id: int
    return_date: datetime  # Campo para mostrar la fecha de la devolución
    class Config:
        from_attributes = True
class ReturnTotalOut(BaseModel):
    total_returned: float  # El total de dinero devuelto en la fecha o rango de fechas