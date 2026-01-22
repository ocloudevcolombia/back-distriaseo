from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.store.returns.models import Return
from app.schemas.store.returns.schemas import ReturnCreate, ReturnUpdate
from datetime import date

# Crear una nueva devolución
def create_return(db: Session, return_in: ReturnCreate):
    new_return = Return(**return_in.model_dump())
    db.add(new_return)
    db.commit()
    db.refresh(new_return)
    return new_return

# Obtener todas las devoluciones
def get_returns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Return).offset(skip).limit(limit).all()

# Obtener una devolución específica por ID
def get_return(db: Session, return_id: int):
    return db.query(Return).filter(Return.id == return_id).first()

# Obtener devoluciones por fecha
def get_returns_by_date(db: Session, return_date: date):
    # Se usa func.date() para comparar solo la fecha, ignorando la hora
    return db.query(Return).filter(func.date(Return.return_date) == return_date).all()

# Obtener el total de devoluciones por fecha
def get_total_returns_by_date(db: Session, return_date: date):
    # Se usa func.date() para comparar solo la fecha
    return db.query(func.sum(Return.amount_returned)).filter(func.date(Return.return_date) == return_date).scalar() or 0

# Obtener devoluciones por rango de fechas
def get_returns_by_date_range(db: Session, start_date: date, end_date: date):
    # Compara las fechas, ignorando la parte de la hora
    return db.query(Return).filter(func.date(Return.return_date) >= start_date, func.date(Return.return_date) <= end_date).all()

# Obtener el total de devoluciones por rango de fechas
def get_total_returns_by_date_range(db: Session, start_date: date, end_date: date):
    # Compara las fechas, ignorando la parte de la hora
    return db.query(func.sum(Return.amount_returned)).filter(func.date(Return.return_date) >= start_date, func.date(Return.return_date) <= end_date).scalar() or 0

# Actualizar una devolución
def update_return(db: Session, return_id: int, return_in: ReturnUpdate):
    db_return = get_return(db, return_id)
    if not db_return:
        return None

    for field, value in return_in.model_dump(exclude_unset=True).items():
        setattr(db_return, field, value)

    db.commit()
    db.refresh(db_return)
    return db_return

# Eliminar una devolución
def delete_return(db: Session, return_id: int):
    db_return = get_return(db, return_id)
    if not db_return:
        return None

    db.delete(db_return)
    db.commit()
    return db_return
