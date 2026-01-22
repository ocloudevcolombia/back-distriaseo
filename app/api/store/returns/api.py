from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.store.returns.schemas import ReturnCreate, ReturnUpdate, ReturnOut,ReturnTotalOut
from app.services.store.returns.services import (
    create_return,
    get_returns,
    get_return,
    update_return,
    delete_return,
    get_returns_by_date,
    get_total_returns_by_date,
    get_returns_by_date_range,
    get_total_returns_by_date_range
)
from datetime import date

returns_router = APIRouter(
    prefix="/returns",
    tags=["Returns"]
)

# Crear una nueva devolución
@returns_router.post("/", response_model=ReturnOut, status_code=status.HTTP_201_CREATED)
def create_return_endpoint(return_in: ReturnCreate, db: Session = Depends(get_db)):
    return create_return(db, return_in)

# Obtener todas las devoluciones
@returns_router.get("/", response_model=list[ReturnOut])
def get_returns_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_returns(db, skip=skip, limit=limit)

# Obtener una devolución específica por ID
@returns_router.get("/{return_id}", response_model=ReturnOut)
def get_return_endpoint(return_id: int, db: Session = Depends(get_db)):
    db_return = get_return(db, return_id)
    if not db_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    return db_return

# Actualizar una devolución
@returns_router.patch("/{return_id}", response_model=ReturnOut)
def update_return_endpoint(return_id: int, return_in: ReturnUpdate, db: Session = Depends(get_db)):
    db_return = update_return(db, return_id, return_in)
    if not db_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    return db_return

# Eliminar una devolución
@returns_router.delete("/{return_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_return_endpoint(return_id: int, db: Session = Depends(get_db)):
    db_return = delete_return(db, return_id)
    if not db_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    return

# Obtener devoluciones por día específico
@returns_router.get("/by_date/{return_date}", response_model=list[ReturnOut])
def get_returns_by_date_endpoint(return_date: date, db: Session = Depends(get_db)):
    return get_returns_by_date(db, return_date)

# Obtener el total de devoluciones por día específico
@returns_router.get("/total_by_date/{return_date}", response_model=ReturnTotalOut)
def get_total_returns_by_date_endpoint(return_date: date, db: Session = Depends(get_db)):
    total_return = get_total_returns_by_date(db, return_date)
    return {"total_returned": total_return}

# Obtener devoluciones por rango de fechas
@returns_router.get("/by_date_range/", response_model=list[ReturnOut])
def get_returns_by_date_range_endpoint(start_date: date, end_date: date, db: Session = Depends(get_db)):
    return get_returns_by_date_range(db, start_date, end_date)

# Obtener el total de devoluciones por rango de fechas
@returns_router.get("/total_by_date_range/", response_model=ReturnTotalOut)
def get_total_returns_by_date_range_endpoint(start_date: date, end_date: date, db: Session = Depends(get_db)):
    total_return = get_total_returns_by_date_range(db, start_date, end_date)
    return {"total_returned": total_return}
