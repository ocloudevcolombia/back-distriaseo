from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.store.services.models import Service
from app.schemas.store.services.schemas import ServiceCreate, ServiceUpdate

def create_service(db: Session, service: ServiceCreate):
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_service(db: Session, service_id: int):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service

def get_all_services(db: Session):
    return db.query(Service).all()

def update_service(db: Session, service_id: int, service: ServiceUpdate):
    db_service = db.get(Service, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    update_data = service.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service, key, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(service)
    db.commit()
    return {"message": "Servicio eliminado"}