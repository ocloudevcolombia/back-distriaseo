from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func
from datetime import date
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from app.models.store.products.models import Product
from app.models.store.sales.models import Sale
from app.models.store.orders.models import Order,OrderItem
from app.schemas.store.sales.schemas import SaleCreate
from app.services.store.returns.services import get_total_returns_by_date


# Funciones auxiliares para cálculos
def _calculate_earnings(order: Order, product_dict: Dict[int, Product]) -> list:
    earnings = []
    for item in order.items:
        product = product_dict.get(item.product_id)
        if not product:
            continue

        quantity = Decimal(str(item.quantity or 0))
        if quantity == 0:
            continue

        purchase_price = Decimal(str(product.purchase_price))
        expected_unit_price = Decimal(str(product.sale_price))
        real_unit_price = Decimal(str(item.price_unit or 0))

        if real_unit_price == 0:
            loss_amount = purchase_price * quantity
            actual_profit_per_unit = Decimal("0.00")
            expected_profit_per_unit = expected_unit_price - purchase_price
            total_actual_profit = Decimal("0.00")
            profit_difference_total = -expected_profit_per_unit * quantity
        else:
            loss_amount = Decimal("0.00")
            actual_profit_per_unit = real_unit_price - purchase_price
            expected_profit_per_unit = expected_unit_price - purchase_price
            total_actual_profit = actual_profit_per_unit * quantity
            profit_difference_total = (actual_profit_per_unit - expected_profit_per_unit) * quantity

        earnings.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "expected_unit_price": expected_unit_price,
            "real_unit_price": real_unit_price,
            "expected_profit_per_unit": expected_profit_per_unit,
            "actual_profit_per_unit": actual_profit_per_unit,
            "total_actual_profit": total_actual_profit,
            "profit_difference_total": profit_difference_total,
            "loss_amount": loss_amount
        })
    return earnings

def _calculate_losses(earnings: list) -> Decimal:
    return Decimal(sum(Decimal(str(e["loss_amount"])) for e in earnings))

def _calculate_returns(db: Session, day: date) -> Decimal:
    returns = get_total_returns_by_date(db=db, return_date=day)
    return Decimal(str(returns)) if returns is not None else Decimal("0.00")

def earnings_by_date_range(
    db: Session,
    start_date: date,
    end_date: date,
    user_id: int = None
) -> Dict[str, Any]:

    query = db.query(Sale).options(
        joinedload(Sale.order).joinedload(Order.items)
    ).filter(
        func.date(Sale.date) >= start_date,
        func.date(Sale.date) <= end_date
    )

    # Filtro por usuario si se envía
    if user_id:
        query = query.join(Sale.order).filter(Order.user_id == user_id)

    sales = query.order_by(Sale.date).all()
        
    earnings_by_product = {}
    daily_breakdown = {}
    total_profit_period = Decimal("0.00")
    total_losses_period = Decimal("0.00")
    total_returns_period = Decimal("0.00")

    product_ids = {
        item.product_id
        for sale in sales
        for item in (sale.order.items if sale.order else [])
    }

    products = (
        db.query(Product).filter(Product.id.in_(product_ids)).all()
        if product_ids else []
    )

    product_dict = {product.id: product for product in products}

    for sale in sales:
        order = sale.order
        if not order or not order.items:
            continue
            
        sale_date = sale.date.date()
        
        if sale_date not in daily_breakdown:
            daily_breakdown[sale_date] = {
                "earnings_by_product": {},
                "total_profit_day": Decimal("0.00"),
                "total_losses_day": Decimal("0.00"),
                "total_returns_day": Decimal("0.00"),
                "net_profit_day": Decimal("0.00")
            }
        
        earnings = _calculate_earnings(order, product_dict)
        
        for e in earnings:
            pid = e["product_id"]
            
            if pid not in daily_breakdown[sale_date]["earnings_by_product"]:
                daily_breakdown[sale_date]["earnings_by_product"][pid] = {
                    "product_name": e["product_name"],
                    "quantity_sold": float(e["quantity"]),
                    "real_unit_price": float(e["real_unit_price"]),
                    "expected_unit_price": float(e["expected_unit_price"]),
                    "purchase_price": float(e["purchase_price"]),
                    "total_actual_profit": float(
                        e["total_actual_profit"].quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    ),
                    "loss": float(
                        e["loss_amount"].quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    )
                }
            else:
                daily_breakdown[sale_date]["earnings_by_product"][pid]["quantity_sold"] += float(e["quantity"])
                daily_breakdown[sale_date]["earnings_by_product"][pid]["total_actual_profit"] += float(
                    e["total_actual_profit"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                )
                daily_breakdown[sale_date]["earnings_by_product"][pid]["loss"] += float(
                    e["loss_amount"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                )
            
            daily_breakdown[sale_date]["total_profit_day"] += e["total_actual_profit"]
            daily_breakdown[sale_date]["total_losses_day"] += e["loss_amount"]
        
        if "returns_calculated" not in daily_breakdown[sale_date]:
            returns = _calculate_returns(db, sale_date)
            daily_breakdown[sale_date]["total_returns_day"] = returns
            daily_breakdown[sale_date]["returns_calculated"] = True
            daily_breakdown[sale_date]["net_profit_day"] = (
                daily_breakdown[sale_date]["total_profit_day"]
                - daily_breakdown[sale_date]["total_losses_day"]
                - returns
            )
    
    for day_data in daily_breakdown.values():
        total_profit_period += day_data["total_profit_day"]
        total_losses_period += day_data["total_losses_day"]
        total_returns_period += day_data["total_returns_day"]
    
    net_profit_after_returns = (
        total_profit_period
        - total_losses_period
        - total_returns_period
    )
    
    for day_data in daily_breakdown.values():
        for pid, product_data in day_data["earnings_by_product"].items():
            if pid not in earnings_by_product:
                earnings_by_product[pid] = {
                    "product_name": product_data["product_name"],
                    "quantity_sold": product_data["quantity_sold"],
                    "real_unit_price": product_data["real_unit_price"],
                    "expected_unit_price": product_data["expected_unit_price"],
                    "purchase_price": product_data["purchase_price"],
                    "total_actual_profit": product_data["total_actual_profit"],
                    "loss": product_data["loss"]
                }

    return {
        "daily_breakdown": {
            str(day): {
                "earnings_by_product": day_data["earnings_by_product"],
                "total_profit_day": float(
                    day_data["total_profit_day"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                ),
                "total_losses_day": float(
                    day_data["total_losses_day"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                ),
                "total_returns_day": float(
                    day_data["total_returns_day"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                ),
                "net_profit_day": float(
                    day_data["net_profit_day"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                )
            }
            for day, day_data in sorted(daily_breakdown.items())
        },
        "summary": {
            "earnings_by_product": earnings_by_product,
            "total_profit_period": float(
                total_profit_period.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "total_losses_period": float(
                total_losses_period.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "total_returns_period": float(
                total_returns_period.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "net_profit_after_returns": float(
                net_profit_after_returns.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days_with_sales": len(daily_breakdown)
        }
    }

def earnings_per_day(day: date, db: Session) -> Dict[str, Any]:
    sales = db.query(Sale).options(
        joinedload(Sale.order).joinedload(Order.items)
    ).filter(func.date(Sale.date) == day).all()
    earnings_by_product = {}
    total_profit_day = Decimal("0.00")

    product_ids = {item.product_id for sale in sales for item in (sale.order.items if sale.order else [])}
    products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    product_dict = {product.id: product for product in products}

    all_earnings = []
    for sale in sales:
        order = sale.order
        if not order or not order.items:
            continue
        earnings = _calculate_earnings(order, product_dict)
        all_earnings.extend(earnings)

    total_losses = _calculate_losses(all_earnings)

    for e in all_earnings:
        pid = e["product_id"]
        if pid not in earnings_by_product:
            earnings_by_product[pid] = {
                "product_name": e["product_name"],
                "quantity_sold": float(e["quantity"]),
                "real_unit_price": float(e["real_unit_price"]),
                "expected_unit_price": float(e["expected_unit_price"]),
                "purchase_price": float(e["purchase_price"]),
                "expected_profit_per_unit": float(e["expected_profit_per_unit"]),
                "actual_profit_per_unit": float(e["actual_profit_per_unit"]),
                "total_actual_profit": float(e["total_actual_profit"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "profit_difference_total": float(e["profit_difference_total"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "loss": float(e["loss_amount"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            }
        else:
            earnings_by_product[pid]["quantity_sold"] += float(e["quantity"])
            earnings_by_product[pid]["total_actual_profit"] += float(e["total_actual_profit"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            earnings_by_product[pid]["profit_difference_total"] += float(e["profit_difference_total"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            earnings_by_product[pid]["loss"] += float(e["loss_amount"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        total_profit_day += e["total_actual_profit"]

    total_profit_day -= total_losses
    total_returns = _calculate_returns(db, day)
    net_profit_after_returns = total_profit_day - total_returns

    return {
        "daily_breakdown": {
            day.isoformat(): {
                "earnings_by_product": earnings_by_product,
                "total_profit_day": float(total_profit_day.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "total_losses_day": float(total_losses.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "total_returns_day": float(total_returns.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "net_profit_day": float(net_profit_after_returns.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            }
        },
        "summary": {
            "earnings_by_product": earnings_by_product,
            "total_profit_period": float(total_profit_day.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "total_losses_period": float(total_losses.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "total_returns_period": float(total_returns.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "net_profit_after_returns": float(net_profit_after_returns.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "start_date": day.isoformat(),
            "end_date": day.isoformat(),
            "days_with_sales": 1 if earnings_by_product else 0
        }
    }

# Funciones CRUD para ventas (sin cambios)
def create_sale(db: Session, sale_data: SaleCreate, user_id: int = None) -> Sale:
    order = db.query(Order).filter(Order.id == sale_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Este pedido ya fue facturado")
    
    # Si el pedido no tiene user_id y se proporciona uno, lo asignamos
    if not order.user_id and user_id:
        order.user_id = user_id

    # Verificar productos y actualizar stock (sin bloquear venta por stock 0)
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        if not product:
            raise HTTPException(
                status_code=404, 
                detail=f"Producto con ID {item.product_id} no encontrado"
            )
            
        # Solo reducir stock si hay suficiente (evitando negativos)
        if product.stock > 0:
            product.stock = max(0, product.stock - item.quantity)  # Asegura que no sea negativo
            db.add(product)

    # Lógica existente para calcular totales
    total = sum(Decimal(str(item.subtotal)) for item in order.items) if order.items else Decimal("0.00")
    transfer_payment = Decimal(str(sale_data.transfer_payment or 0))
    balance = total - transfer_payment

    # Crear la venta
    sale = Sale(
        order_id=order.id,
        total=float(total),
        transfer_payment=float(transfer_payment),
        balance=float(balance)
    )
    
    db.add(sale)
    order.status = "completed"
    db.commit()
    db.refresh(order)
    db.refresh(sale)

    return sale
def get_all_sales(db: Session):
    return db.query(Sale).options(
        joinedload(Sale.order)
        .joinedload(Order.items)
        .joinedload(OrderItem.product)
    ).all()

def get_sale_by_id(db: Session, sale_id: int) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale

def get_sales_by_customer(db: Session, customer_id: int):
    return (
        db.query(Sale)
        .join(Sale.order)
        .filter(Order.customer_id == customer_id)
        .order_by(Sale.date.desc())
        .all()
    )

def update_sale(db: Session, sale_id: int, sale_data: SaleCreate) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    # No permitimos cambiar el pedido asociado, solo los pagos
    transfer_payment = Decimal(str(sale_data.transfer_payment or sale.transfer_payment))
    total = Decimal(str(sale.total))
    balance = total - transfer_payment

    sale.transfer_payment = float(transfer_payment)
    sale.balance = float(balance)

    db.commit()
    db.refresh(sale)

    return sale

def delete_sale(db: Session, sale_id: int) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    # Restaurar el stock de los productos
    order = sale.order
    if order:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
            if product:
                product.stock += item.quantity
                db.add(product)

    db.delete(sale)
    db.commit()

    return sale

def sales_for_day(db: Session, day: date):
    return db.query(Sale).filter(func.date(Sale.date) == day).all()

def sales_between_dates(db: Session, start_date: date, end_date: date):
    return db.query(Sale).filter(
        func.date(Sale.date) >= start_date,
        func.date(Sale.date) <= end_date
    ).all()