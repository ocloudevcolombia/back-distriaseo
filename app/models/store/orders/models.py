from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime,Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from app.models.store.customers.models import Customer
from app.models.store.products.models import Product
import pytz

# 🧾 PEDIDO (Order)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ID del usuario que creó el pedido
    date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))  # Fecha de la devolución ajustada a Colombia
    status = Column(String(20), default="pending")  # Puede ser: "pending", "confirmed", "canceled"

    # Relaciones
    customer = relationship(Customer, backref="orders")  # Relación con Customer
    user = relationship("User", backref="orders")  # Relación con User (quien creó el pedido)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")  # Relación con OrderItem

# 📦 DETALLE DE PEDIDO (Order Item)
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Numeric(7,3), nullable=False)
    price_unit = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    observaciones = Column(String(255), nullable=True)

    # Relaciones
    order = relationship("Order", back_populates="items")  # Relación con Order
    product = relationship(Product)  # Relación con Product
