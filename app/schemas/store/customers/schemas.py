from pydantic import BaseModel
from typing import Optional

# Esquema base con los campos comunes
class CustomerBase(BaseModel):
    name: str
    cc: int
    alias: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str]=None
    direction: Optional[str] = None

# Esquema para crear un nuevo cliente
class CustomerCreate(CustomerBase):
    pass

# Esquema para actualizar el cliente (todos los campos son opcionales para un PATCH)
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    cc: Optional[int] = None
    alias: Optional[str] = None
    avatar: Optional[str]=None
    phone: Optional[str] = None
    direction: Optional[str] = None

    class Config:
        # Permite trabajar con modelos ORM
        from_attributes = True

# Esquema de salida para devolver los datos del cliente
class CustomerOut(CustomerBase):
    id: int
    

    class Config:
        from_attributes = True
