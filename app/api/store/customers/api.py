# api/customers.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.store.customers.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from app.services.store.customers.services import create_customer, get_customer_by_id, get_all_customers, update_customer, delete_customer

customers_router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@customers_router.post("/", response_model=CustomerOut)
def create_customer_endpoint(customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo cliente.
    """
    return create_customer(db, customer)

@customers_router.get("/", response_model=List[CustomerOut])
def get_customers_endpoint(db: Session = Depends(get_db)):
    """
    Retorna una lista de todos los clientes.
    """
    return get_all_customers(db)

@customers_router.get("/{customer_id}", response_model=CustomerOut)
def get_customer_endpoint(customer_id: int, db: Session = Depends(get_db)):
    """
    Retorna los datos de un cliente según su ID.
    """
    return get_customer_by_id(db, customer_id)

@customers_router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer_endpoint(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """
    Actualiza parcialmente los datos de un cliente.
    """
    return update_customer(db, customer_id, customer)

@customers_router.delete("/{customer_id}", response_model=CustomerOut)
def delete_customer_endpoint(customer_id: int, db: Session = Depends(get_db)):
    """
    Elimina un cliente.
    """
    return delete_customer(db, customer_id)
