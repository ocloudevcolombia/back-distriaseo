# services/customers.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.store.customers.models import Customer
from app.schemas.store.customers.schemas import CustomerCreate, CustomerUpdate

def create_customer(db: Session, customer_data: CustomerCreate) -> Customer:
    customer = Customer(
        name=customer_data.name,
        cc=customer_data.cc,
        alias=customer_data.alias,
        avatar=customer_data.avatar,
        phone=customer_data.phone,
        direction=customer_data.direction
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def get_customer_by_id(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer

def get_all_customers(db: Session):
    return db.query(Customer).all()

def update_customer(db: Session, customer_id: int, customer_data: CustomerUpdate) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    update_data = customer_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
    
    db.commit()
    db.refresh(customer)
    return customer

def delete_customer(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(customer)
    db.commit()
    return customer
