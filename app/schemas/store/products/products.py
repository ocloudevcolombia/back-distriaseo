from pydantic import BaseModel
from typing import Optional
from app.models.store.products.models import UnidadMedidaEnum

# 💕 CATEGORÍA (se mantiene igual)
class CreateCategory(BaseModel):
    name: str
    description: Optional[str] = None

class UpdateCategory(BaseModel):
    name: str
    description: Optional[str] = None

class ResponseCategory(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

# 🍓 PRODUCTO (actualizado)
class CreateProduct(BaseModel):
    name: Optional[str] = None
    state: Optional[bool] = True
    purchase_price: Optional[float] = None
    stock:  Optional[float] = None
    sale_price: Optional[float] = None
    profit_percentage: Optional[float] = 30.00
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    unit: Optional[UnidadMedidaEnum] = UnidadMedidaEnum.und

    class Config:
        use_enum_values = True

class UpdateProduct(BaseModel):
    name: Optional[str] = None
    state: Optional[bool] = None
    purchase_price: Optional[float] = None
    stock: Optional[float] = None  # Nuevo campo
    sale_price: Optional[float] = None
    profit_percentage: Optional[float] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    unit: Optional[UnidadMedidaEnum] = None

class ResponseProduct(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    state: Optional[bool] = None
    purchase_price: Optional[float] = None
    stock: Optional[float] = None  # Nuevo campo
    sale_price: Optional[float] = None
    profit_percentage: Optional[float] = None
    image_url: Optional[str] = None
    unit: Optional[UnidadMedidaEnum] = None
    category_id: Optional[int] = None
    category: Optional[ResponseCategory] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class ProductOut(BaseModel):
    id: int
    name: str
    state: bool
    purchase_price: float
    stock: Optional[float]  # Nuevo campo
    sale_price: float
    profit_percentage: float
    image_url: Optional[str]
    category_id: Optional[int]
    category: Optional[ResponseCategory]
    unit: UnidadMedidaEnum

    class Config:
        from_attributes = True
        use_enum_values = True