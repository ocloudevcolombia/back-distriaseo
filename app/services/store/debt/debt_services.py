from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.schemas.store.debt.schemas import MovementType
from app.models.store.debt.models import Debt, DebtMovement
from app.schemas.store.debt.schemas import (
    DebtCreate,
    DebtOut,
    DebtUpdate,
    DebtWithMovements,
    MovementCreate,
    MovementOut,
    MovementResult,
    MovementFilters,
    CustomerBalanceHistory
)

class DebtService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_debts(self, with_movements: bool = False) -> List[DebtOut]:
            """Obtiene todas las deudas registradas"""
            debts = self.db.query(Debt).order_by(Debt.updated_at.desc()).all()
            
            if with_movements:
                return [DebtWithMovements.model_validate(debt) for debt in debts]
            else:
                return [DebtOut.model_validate(debt) for debt in debts]

    def create_debt(self, debt_data: DebtCreate) -> DebtOut:
        """Crea una nueva deuda para un cliente"""
        # Verificar si el cliente ya tiene una deuda
        existing_debt = self.db.query(Debt).filter(
            Debt.customer_id == debt_data.customer_id
        ).first()
        
        if existing_debt:
            raise ValueError("El cliente ya tiene una deuda registrada")
        
        new_debt = Debt(
            customer_id=debt_data.customer_id,
            current_balance=debt_data.initial_balance,  # Aquí se establece el balance inicial
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.db.add(new_debt)
        self.db.commit()
        self.db.refresh(new_debt)
    
        return DebtOut.model_validate(new_debt)

    def get_debt(self, debt_id: int) -> Optional[DebtWithMovements]:
        """Obtiene una deuda con sus movimientos"""
        debt = self.db.query(Debt).filter(Debt.id == debt_id).first()
        return DebtWithMovements.model_validate(debt) if debt else None

    def get_debt_by_customer(self, customer_id: int) -> Optional[DebtWithMovements]:
        """Obtiene la deuda de un cliente con sus movimientos"""
        debt = self.db.query(Debt).filter(Debt.customer_id == customer_id).first()
        return DebtWithMovements.model_validate(debt) if debt else None
    
    def delete_debt(self, debt_id: int) -> bool:
        """Elimina una deuda y sus movimientos"""
        debt = self.db.query(Debt).filter(Debt.id == debt_id).first()
        if not debt:
            return False
        
        # Eliminar movimientos asociados
        self.db.query(DebtMovement).filter(DebtMovement.debt_id == debt_id).delete()
        
        self.db.delete(debt)
        self.db.commit()
        return True

    def _create_movement(self, debt_id: int, movement_type: MovementType, 
                        amount: float, description: str = None, notes: str = None) -> MovementOut:
        """Crea un movimiento y actualiza el saldo de la deuda"""
        debt = self.db.query(Debt).filter(Debt.id == debt_id).with_for_update().first()
        if not debt:
            raise ValueError("Deuda no encontrada")
        
        # Crear el movimiento
        new_movement = DebtMovement(
            debt_id=debt_id,
            movement_type=movement_type,
            amount=amount,
            description=description,
            notes=notes,
            movement_date=datetime.now()
        )
        self.db.add(new_movement)
        
        # Actualizar el saldo de la deuda
        if movement_type == MovementType.PAYMENT:
            debt.current_balance -= amount
        else:  # NEW_BALANCE
            debt.current_balance += amount
        
        debt.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(new_movement)
        
        return MovementOut.model_validate(new_movement)

    def register_movement(self, debt_id: int, movement_data: MovementCreate) -> MovementResult:
        """Registra un nuevo movimiento para una deuda"""
        # Validar el tipo de movimiento
        if movement_data.movement_type == MovementType.PAYMENT:
            debt = self.db.query(Debt).filter(Debt.id == debt_id).first()
            if not debt:
                raise ValueError("Deuda no encontrada")
            if movement_data.amount > debt.current_balance:
                raise ValueError("El monto del pago excede el saldo actual")
        
        movement = self._create_movement(
            debt_id=debt_id,
            movement_type=movement_data.movement_type,
            amount=movement_data.amount,
            description=movement_data.description,
            notes=movement_data.notes
        )
        
        debt = self.db.query(Debt).filter(Debt.id == debt_id).first()
        return MovementResult(
            debt=DebtOut.model_validate(debt),
            movement=movement,
            new_balance=debt.current_balance
        )

    def list_movements(self, filters: MovementFilters = None) -> List[MovementOut]:
        """Lista movimientos con filtros opcionales"""
        query = self.db.query(DebtMovement)
        
        if filters:
            if filters.debt_id:
                query = query.filter(DebtMovement.debt_id == filters.debt_id)
            if filters.movement_type:
                query = query.filter(DebtMovement.movement_type == filters.movement_type)
            if filters.min_amount:
                query = query.filter(DebtMovement.amount >= filters.min_amount)
            if filters.max_amount:
                query = query.filter(DebtMovement.amount <= filters.max_amount)
            if filters.date_from:
                query = query.filter(DebtMovement.movement_date >= filters.date_from)
            if filters.date_to:
                query = query.filter(DebtMovement.movement_date <= filters.date_to)
        
        movements = query.order_by(DebtMovement.movement_date.desc()).all()
        return [MovementOut.model_validate(m) for m in movements]

    def delete_movement(self, movement_id: int) -> bool:
        """Elimina un movimiento y ajusta el saldo de la deuda"""
        # Bloquear registros para evitar condiciones de carrera
        movement = self.db.query(DebtMovement).filter(
            DebtMovement.id == movement_id
        ).with_for_update().first()
        
        if not movement:
            return False
        
        debt = self.db.query(Debt).filter(
            Debt.id == movement.debt_id
        ).with_for_update().first()
        
        if not debt:
            return False
        
        # Lógica corregida para ambos tipos de movimiento
        if movement.movement_type == MovementType.PAYMENT:
            # Revertir un PAGO: sumar el monto al saldo (aumenta la deuda)
            debt.current_balance += movement.amount
        elif movement.movement_type == MovementType.NEW_BALANCE:
            # Revertir un INCREMENTO: restar el monto al saldo (disminuye la deuda)
            debt.current_balance -= movement.amount
        
        # Validación de saldo mínimo
        if debt.current_balance < 0:
            # Puedes elegir entre estas opciones:
            # 1. Poner el saldo en cero
            debt.current_balance = 0
            
            # 2. Lanzar una excepción
            # raise ValueError("El saldo no puede ser negativo")
            
            # 3. Permitir saldos negativos si es válido en tu modelo de negocio
        
        # Actualizar marca de tiempo
        debt.updated_at = datetime.now()
        
        # Eliminar el movimiento
        self.db.delete(movement)
        self.db.commit()
        
        return True

    def get_balance_history(self, customer_id: int) -> List[CustomerBalanceHistory]:
        """Obtiene el historial de balance para un cliente"""
        debt = self.db.query(Debt).filter(Debt.customer_id == customer_id).first()
        if not debt:
            return []
        
        # Obtener todos los movimientos ordenados por fecha
        movements = self.db.query(DebtMovement).filter(
            DebtMovement.debt_id == debt.id
        ).order_by(DebtMovement.movement_date).all()
        
        history = []
        current_balance = 0.0
        
        # Reconstruir el historial
        for mov in movements:
            if mov.movement_type == MovementType.PAYMENT:
                current_balance -= mov.amount
            else:
                current_balance += mov.amount
            
            history.append(CustomerBalanceHistory(
                date=mov.movement_date,
                balance=current_balance,
                movement_type=mov.movement_type,
                movement_amount=mov.amount,
            ))
        
        return history
    # Añadir este método a la clase DebtService
    def update_debt(
        self, 
        debt_id: int, 
        update_data: DebtUpdate,
        adjustment_description: str = "Ajuste manual de saldo"
    ) -> DebtOut:
        """Actualiza una deuda existente (PATCH)"""
        debt = self.db.query(Debt).filter(Debt.id == debt_id).with_for_update().first()
        if not debt:
            raise ValueError("Deuda no encontrada")
        
        # Si se está modificando el saldo directamente
        if update_data.current_balance is not None:
            difference = update_data.current_balance - debt.current_balance
            
            # Registrar movimiento de ajuste
            if difference != 0:
                movement_type = (
                    MovementType.NEW_BALANCE if difference > 0 
                    else MovementType.PAYMENT
                )
                
                description = (
                    update_data.description or adjustment_description
                )
                
                self._create_movement(
                    debt_id=debt.id,
                    movement_type=movement_type,
                    amount=abs(difference),
                    description=description,
                    notes="Ajuste manual de saldo"
                )
        
        debt.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(debt)
        
        return DebtOut.model_validate(debt)

    # Modificar el método get_debt para incluir last_movement_date
    def get_debt(self, debt_id: int) -> Optional[DebtWithMovements]:
        """Obtiene una deuda con sus movimientos"""
        debt = self.db.query(Debt).filter(Debt.id == debt_id).first()
        if not debt:
            return None
        
        # Obtener la fecha del último movimiento
        last_movement = self.db.query(func.max(DebtMovement.movement_date)).filter(
            DebtMovement.debt_id == debt_id
        ).scalar()
        
        debt_dict = DebtOut.model_validate(debt).model_dump()
        debt_dict["last_movement_date"] = last_movement
        
        return DebtWithMovements(**debt_dict)