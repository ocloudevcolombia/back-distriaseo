from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.store.services.schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from app.services.store.services.services import (
    create_service,
    get_service,
    get_all_services,
    update_service,
    delete_service
)

services_router = APIRouter(prefix="/services", tags=["Services"])

@services_router.post("/", response_model=ServiceResponse)
def create_new_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db, service)

@services_router.get("/{service_id}", response_model=ServiceResponse)
def read_service(service_id: int, db: Session = Depends(get_db)):
    return get_service(db, service_id)

@services_router.get("/", response_model=list[ServiceResponse])
def read_all_services(db: Session = Depends(get_db)):
    return get_all_services(db)

@services_router.patch("/{service_id}", response_model=ServiceResponse)
def update_existing_service(service_id: int, service: ServiceUpdate, db: Session = Depends(get_db)):
    return update_service(db, service_id, service)

@services_router.delete("/{service_id}")
def delete_existing_service(service_id: int, db: Session = Depends(get_db)):
    return delete_service(db, service_id)