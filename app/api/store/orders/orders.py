from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.users.users import User
from typing import List
from app.schemas.store.orders.schemas import OrderCreate, OrderUpdate, OrderOut
from app.services.store.orders.orders import create_order,patch_order, get_all_orders, get_orders_today, get_order_by_id, update_order, delete_order

orders_router = APIRouter(prefix="/orders", tags=["Orders"])

@orders_router.post("/", response_model=OrderOut)
def create_new_order(
    order: OrderCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Guardamos el ID del usuario logueado en el pedido
    return create_order(db, order, user_id=current_user.id)

@orders_router.get("/", response_model=List[OrderOut])
def get_orders(db: Session = Depends(get_db)):
    return get_all_orders(db)

@orders_router.get("/today", response_model=List[OrderOut])
def get_orders_today_endpoint(db: Session = Depends(get_db)):
    """Obtiene las órdenes del día actual + órdenes pendientes de todos los días"""
    return get_orders_today(db)

@orders_router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return get_order_by_id(db, order_id)

@orders_router.put("/{order_id}", response_model=OrderOut)
def update_order_details(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    return update_order(db, order_id, order_update)

@orders_router.patch("/{order_id}", response_model=OrderOut)
def patch_order_details(order_id: int, order_patch: OrderUpdate, db: Session = Depends(get_db)):
    return patch_order(db, order_id, order_patch)

@orders_router.delete("/{order_id}")
def delete_order_details(order_id: int, db: Session = Depends(get_db)):
    return delete_order(db, order_id)



