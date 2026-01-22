from decimal import Decimal
from pydantic import BaseModel,Field
from typing import List, Optional
from datetime import datetime
from app.schemas.store.customers.schemas import CustomerOut
from app.schemas.store.products.products import ProductOut
from app.schemas.users.users import UserOut

# Esquema para Item del Pedido (OrderItem) al crear
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(max_digits=7, decimal_places=3)
    price_unit: float

    class Config:
        from_attributes = True  # Esto permite que Pydantic use los datos del modelo ORM (SQLAlchemy)

class OrderItemUpdate(BaseModel):
    product_id: Optional[int]
    quantity: Decimal = Field(max_digits=7, decimal_places=3)
    price_unit: Optional[float]

# Esquema para Item del Pedido (OrderItem) en la respuesta
class OrderItemOut(OrderItemCreate):
    subtotal: float  # Calculamos el subtotal del item
    product: ProductOut
    class Config:
        from_attributes = True  # Esto permite que Pydantic use los datos del modelo ORM (SQLAlchemy)


# Esquema para crear un Pedido (Order)
class OrderCreate(BaseModel):
    customer_id: int  # El ID del cliente
    items: List[OrderItemCreate]  # Lista de los items del pedido (OrderItems)

    class Config:
        from_attributes = True  # Permite que se use la base de datos como fuente de datos

# Esquema para mostrar el Pedido (Order) con los detalles de los items
class OrderOut(BaseModel):
    id: int  # ID del pedido
    customer: Optional[CustomerOut]
    user: Optional[UserOut]  # Usuario que creó el pedido
    date: datetime  # Fecha del pedido (en formato string ISO)
    status: str  # Estado del pedido (puede ser: "pending", "confirmed", "canceled")
    items: List[OrderItemOut]  # Lista de items del pedido

    class Config:
        from_attributes = True  # Permite que se use la base de datos como fuente de datos

# Esquema para actualizar un Pedido (Order)
class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    items: Optional[List[OrderItemUpdate]] = None

    class Config:
        from_attributes = True