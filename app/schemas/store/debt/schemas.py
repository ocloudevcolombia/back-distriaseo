from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum
from app.models.store.debt.models import Debt,DebtMovement

class MovementType(str, Enum):
    PAYMENT = "PAYMENT"
    NEW_BALANCE = "NEW_BALANCE"

# -------------------------
# Esquemas para Deudas (Debt)
# -------------------------

class DebtBase(BaseModel):
    customer_id: int = Field(..., gt=0, description="ID del cliente asociado")

class DebtCreate(DebtBase):
    """Esquema para creación de deudas"""
    initial_balance: float = Field(0.0, ge=0, description="Saldo inicial de la deuda")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "customer_id": 1,
            "initial_balance": 1500.00
        }
    })

# Añadir este esquema para actualización de deuda
class DebtUpdate(BaseModel):
    """Esquema para actualización parcial de deuda"""
    current_balance: Optional[float] = Field(
        None, 
        ge=0, 
        description="Nuevo saldo actual. Usar solo para correcciones"
    )
    description: Optional[str] = Field(
        None,
        max_length=100,
        description="Motivo de la modificación del saldo"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "current_balance": 2500.00,
            "description": "Corrección de saldo por error en registro inicial"
        }
    })

# Modificar DebtOut para incluir más información
class DebtOut(DebtBase):
    """Esquema para respuesta de deudas"""
    id: int
    current_balance: float = Field(..., description="Saldo actual (lo que debe actualmente)")
    created_at: datetime
    updated_at: datetime
    last_movement_date: Optional[datetime] = Field(
        None,
        description="Fecha del último movimiento registrado"
    )
    
    model_config = ConfigDict(from_attributes=True)
# -------------------------
# Esquemas para Movimientos
# -------------------------

class MovementBase(BaseModel):
    amount: float = Field(..., gt=0, description="Monto del movimiento")
    movement_type: MovementType = Field(..., description="Tipo de movimiento")
    description: Optional[str] = Field(None, max_length=255, description="Descripción breve")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

class MovementCreate(MovementBase):
    """Esquema para creación de movimientos"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "amount": 500.00,
            "movement_type": "PAYMENT",
            "description": "Pago en efectivo",
            "notes": "Recibido por caja principal"
        }
    })

class MovementOut(MovementBase):
    """Esquema para respuesta de movimientos"""
    id: int
    debt_id: int
    movement_date: datetime
    
    model_config = ConfigDict(from_attributes=True)

# -------------------------
# Esquemas Combinados
# -------------------------

class DebtWithMovements(DebtOut):
    """Deuda con lista de movimientos asociados"""
    movements: List[MovementOut] = []
    
    model_config = ConfigDict(from_attributes=True)

class MovementResult(BaseModel):
    """Resultado detallado después de registrar un movimiento"""
    debt: DebtOut
    movement: MovementOut
    new_balance: float = Field(..., description="Nuevo saldo después del movimiento")
    remaining_debt: float = Field(
        ...,
        description="Lo que queda debiendo (alias de new_balance para claridad)",
        alias="new_balance"  # Esto hace que new_balance también sirva como remaining_debt
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # Permite usar tanto el nombre del campo como su alias
    )

    @classmethod
    def create_from_objects(cls, debt: Debt, movement: DebtMovement):
        """Factory method para crear el resultado desde objetos ORM"""
        debt_out = DebtOut.model_validate(debt)
        movement_out = MovementOut.model_validate(movement)
        
        return cls(
            debt=debt_out,
            movement=movement_out,
            new_balance=debt.current_balance
            # remaining_debt se llena automáticamente por el alias
        )
# -------------------------
# Esquemas para Consultas/Filtros
# -------------------------

class MovementFilters(BaseModel):
    """Filtros para consulta de movimientos"""
    debt_id: Optional[int] = None
    movement_type: Optional[MovementType] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

# -------------------------
# Esquemas para Estadísticas
# -------------------------

class CustomerBalanceHistory(BaseModel):
    """Historial de balance para un cliente"""
    date: datetime
    balance: float
    movement_type: Optional[MovementType] = None
    movement_amount: Optional[float] = None