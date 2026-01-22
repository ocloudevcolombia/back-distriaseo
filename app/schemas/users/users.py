from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):

    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str]
    direction: Optional[str] = None
    image: Optional[str]=None
    rol: Optional[str] = "user"  # Campo opcional, por defecto "user"

    
class UserRead(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str]
    direction: Optional[str] = None
    image: Optional[str]=None
    rol: Optional[str] = None

    class Config:
        from_attributes=True

# Esquema de salida para devolver los datos del usuario en órdenes
class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str]
    direction: Optional[str] = None
    image: Optional[str]=None
    rol: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    direction: Optional[str] = None
    image: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None

    class Config:
        from_attributes = True