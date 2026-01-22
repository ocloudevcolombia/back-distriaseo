from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from app.models.store.orders.models import Order
import pytz


# 💸 VENTA (Sale)
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))  # Fecha de la devolución ajustada a Colombia
    transfer_payment = Column(Float, default=0.0, nullable=True)
    total = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)

    # Relaciones
    order = relationship(Order, backref="sale")
