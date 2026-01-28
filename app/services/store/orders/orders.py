from sqlalchemy.orm import Session,joinedload
from fastapi import HTTPException, status
from app.models.store.orders.models import Order, OrderItem
from app.schemas.store.orders.schemas import OrderCreate, OrderUpdate, OrderOut, OrderItemCreate
from app.models.store.sales.models import Sale
from sqlalchemy import select
from decimal import Decimal
from datetime import datetime, date
import pytz

# Servicio para crear un pedido (Order)
def create_order(db: Session, order: OrderCreate, user_id: int = None):
    # Primero creamos los items de pedido (OrderItems)
    order_items = []
    for item in order.items:
        subtotal = item.quantity * Decimal(str(item.price_unit))
        order_item = OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price_unit=item.price_unit,
            subtotal=subtotal
        )
        order_items.append(order_item)

    # Creamos el pedido (Order) y asociamos los items
    db_order = Order(
        customer_id=order.customer_id,
        user_id=user_id,  # Guardamos el ID del usuario que creó el pedido
        status="pending",  # Por defecto el estado será "pending"
        items=order_items
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Retornar el pedido con las relaciones cargadas
    return db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.customer),
        joinedload(Order.user)
    ).filter(Order.id == db_order.id).first()


# Servicio para obtener todos los pedidos (Order)
def get_all_orders(db: Session, user_id: int = None):
    query = db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.customer),
        joinedload(Order.user)
    )

    # Si no es admin, filtramos por usuario
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)

    return query.all()


# Servicio para obtener las órdenes del día actual + órdenes pendientes de todos los días
def get_orders_today(db: Session, user_id: int = None):
    colombia_tz = pytz.timezone('America/Bogota')
    today = datetime.now(colombia_tz).date()

    start_of_day = colombia_tz.localize(datetime.combine(today, datetime.min.time()))
    end_of_day = colombia_tz.localize(datetime.combine(today, datetime.max.time()))

    from sqlalchemy import or_, and_

    query = db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.customer),
        joinedload(Order.user)
    ).filter(
        or_(
            (Order.date >= start_of_day) & (Order.date <= end_of_day),
            Order.status == "pending"
        )
    )

    # Si no es admin, filtrar por usuario
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)

    return query.all()


# Servicio para obtener un pedido específico (Order)
def get_order_by_id(db: Session, order_id: int, user_id: int = None):
    query = db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.customer),
        joinedload(Order.user)
    ).filter(Order.id == order_id)

    # Si no es admin, solo puede ver su orden
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)

    db_order = query.first()

    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or access denied"
        )

    return db_order

# Servicio para actualizar un pedido (Order)
def update_order(db: Session, order_id: int, order_update: OrderUpdate):
    # Obtenemos el pedido actual para actualizarlo
    db_order = db.query(Order).filter(Order.id == order_id).first()

    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Actualizamos los campos del pedido
    if order_update.customer_id:
        db_order.customer_id = order_update.customer_id
    if order_update.status:
        db_order.status = order_update.status
    if order_update.items:
        # Primero eliminamos los items existentes y agregamos los nuevos
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        for item in order_update.items:
            subtotal = item.quantity * Decimal(str(item.price_unit))
            order_item = OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_unit=item.price_unit,
                subtotal=subtotal,
                order_id=db_order.id
            )
            db.add(order_item)

    db.commit()
    db.refresh(db_order)
    
    # Retornar el pedido con las relaciones cargadas
    return db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.customer),
        joinedload(Order.user)
    ).filter(Order.id == order_id).first()

# Servicio para hacer un patch (actualización parcial) de un pedido (Order)
def patch_order(db: Session, order_id: int, order_patch: OrderUpdate):
    db_order = db.query(Order).filter(Order.id == order_id).first()

    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Solo actualizamos los campos que vengan en el request
    if order_patch.customer_id is not None:
        db_order.customer_id = order_patch.customer_id
    if order_patch.status is not None:
        db_order.status = order_patch.status
    if order_patch.items is not None:
        # Eliminamos los items anteriores
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        for item in order_patch.items:
            subtotal = item.quantity * Decimal(str(item.price_unit))
            order_item = OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_unit=item.price_unit,
                subtotal=subtotal,
                order_id=db_order.id
            )
            db.add(order_item)

    db.commit()
    db.refresh(db_order)
    
    # Retornar el pedido con las relaciones cargadas
    return db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.customer),
        joinedload(Order.user)
    ).filter(Order.id == order_id).first()


# Servicio para borrar un pedido (Order)
def delete_order(db: Session, order_id: int):
    # Obtenemos el pedido para borrarlo
    db_order = db.query(Order).filter(Order.id == order_id).first()

    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Borramos los items del pedido
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    
    # Borramos el pedido
    db.delete(db_order)
    db.commit()
    
    return {"message": "Order deleted successfully"}
