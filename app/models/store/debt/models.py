from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Text, Enum, String
from datetime import datetime
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum as PyEnum
import pytz

class MovementType(PyEnum):
    PAYMENT = "PAYMENT"       # Abono a la deuda
    NEW_BALANCE = "NEW_BALANCE" # Aumento de la deuda (nuevo saldo)

class Debt(Base):
    __tablename__ = "debts"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, unique=True)
    current_balance = Column(Float, default=0.0, nullable=False)  # Saldo actual
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))
    
    # Relación con movimientos
    movements = relationship("DebtMovement", back_populates="debt", order_by="DebtMovement.movement_date.desc()")

class DebtMovement(Base):
    __tablename__ = "debt_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(Integer, ForeignKey("debts.id"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    amount = Column(Float, nullable=False)
    movement_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))
    description = Column(String(255))
    notes = Column(Text)
    
    debt = relationship("Debt", back_populates="movements")