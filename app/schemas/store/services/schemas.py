from pydantic import BaseModel
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    price: float  # FastAPI convertirá automáticamente a Decimal/Numeric

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None

class ServiceResponse(ServiceBase):
    id: int

    class Config:
        from_attributes = True  # Habilita la compatibilidad con ORM