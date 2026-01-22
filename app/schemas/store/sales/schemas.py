from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.store.orders.schemas import OrderOut

# 💸 VENTA (SALE)
class SaleCreate(BaseModel):
    order_id: int
    transfer_payment: Optional[float] = 0.0
    balance: Optional[float] = 0.0

    class Config:
        from_attributes = True

class SaleOut(BaseModel):
    id: Optional[int]
    order_id: Optional[int]
    date: datetime
    total: float
    transfer_payment: Optional[float] = 0.0
    balance: Optional[float] = 0.0
    order: Optional[OrderOut]  # ← Agregas esto

    class Config:
        from_attributes = True
