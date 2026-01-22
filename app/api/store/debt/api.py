from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.store.debt.models import DebtMovement
from app.core.database import get_db
from app.schemas.store.debt.schemas import (
    DebtCreate,
    DebtOut,
    DebtUpdate,
    DebtWithMovements,
    MovementCreate,
    MovementOut,
    MovementResult,
    MovementFilters,
    CustomerBalanceHistory)
from app.services.store.debt.debt_services import DebtService

debts_router = APIRouter(prefix="/debts", tags=["Debts Management"])

# -------------------------
# Endpoints para Deudas
# -------------------------

@debts_router.get("/", response_model=List[DebtOut])
def get_all_debts(
    with_movements: bool = False,
    db: Session = Depends(get_db)
):
    """Obtiene todas las deudas registradas"""
    return DebtService(db).get_all_debts(with_movements)

@debts_router.post("/", response_model=DebtOut, status_code=status.HTTP_201_CREATED)
def create_debt(debt_data: DebtCreate, db: Session = Depends(get_db)):
    """Crea una nueva deuda para un cliente"""
    try:
        return DebtService(db).create_debt(debt_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@debts_router.get("/{debt_id}", response_model=DebtWithMovements)
def get_debt(debt_id: int, db: Session = Depends(get_db)):
    """Obtiene una deuda específica con sus movimientos"""
    debt = DebtService(db).get_debt(debt_id)
    if not debt:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    return debt

@debts_router.get("/customer/{customer_id}", response_model=DebtWithMovements)
def get_debt_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Obtiene la deuda de un cliente con sus movimientos"""
    debt = DebtService(db).get_debt_by_customer(customer_id)
    if not debt:
        raise HTTPException(status_code=404, detail="El cliente no tiene deuda registrada")
    return debt

@debts_router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_debt(debt_id: int, db: Session = Depends(get_db)):
    """Elimina una deuda y sus movimientos asociados"""
    if not DebtService(db).delete_debt(debt_id):
        raise HTTPException(status_code=404, detail="Deuda no encontrada")

# -------------------------
# Endpoints para Movimientos
# -------------------------

@debts_router.post("/{debt_id}/movements", response_model=MovementResult, status_code=status.HTTP_201_CREATED)
def register_movement(
    debt_id: int, 
    movement_data: MovementCreate, 
    db: Session = Depends(get_db)
):
    """Registra un nuevo movimiento (abono o nuevo saldo)"""
    try:
        return DebtService(db).register_movement(debt_id, movement_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@debts_router.get("/movements/{movement_id}", response_model=MovementOut)
def get_movement(movement_id: int, db: Session = Depends(get_db)):
    """Obtiene un movimiento específico"""
    movement = db.query(DebtMovement).filter(DebtMovement.id == movement_id).first()
    if not movement:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return MovementOut.model_validate(movement)

@debts_router.get("/{debt_id}/movements", response_model=List[MovementOut])
def list_debt_movements(
    debt_id: int,
    movement_type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Lista todos los movimientos de una deuda"""
    filters = MovementFilters(
        debt_id=debt_id,
        movement_type=movement_type,
        min_amount=min_amount,
        max_amount=max_amount,
        date_from=date_from,
        date_to=date_to
    )
    return DebtService(db).list_movements(filters)

@debts_router.delete("/movements/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movement(movement_id: int, db: Session = Depends(get_db)):
    """Elimina un movimiento y ajusta el saldo de la deuda correspondiente"""
    if not DebtService(db).delete_movement(movement_id):
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

@debts_router.get("/customer/{customer_id}/history", response_model=List[CustomerBalanceHistory])
def get_customer_balance_history(customer_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial completo de balance para un cliente"""
    return DebtService(db).get_balance_history(customer_id)

@debts_router.patch("/{debt_id}", response_model=DebtOut)
def update_debt(
    debt_id: int,
    update_data: DebtUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una deuda existente (solo campos proporcionados)"""
    try:
        return DebtService(db).update_debt(debt_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))