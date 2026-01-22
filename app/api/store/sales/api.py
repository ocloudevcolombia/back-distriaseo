from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.users.users import User
from app.schemas.store.sales.schemas import SaleCreate, SaleOut
from decimal import Decimal
from app.services.store.sales.services import (
    create_sale,
    get_all_sales,
    get_sale_by_id,
    get_sales_by_customer,
    update_sale,
    delete_sale,
    sales_for_day,
    sales_between_dates,
    earnings_per_day,
    earnings_by_date_range
)

sales_router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)

# ------------------ Esquemas de Métricas ------------------

class ProfitMarginOut(BaseModel):
    product_name: str
    margin: float

class SalesMetrics(BaseModel):
    total_sales: float
    total_quantity: Decimal
    most_sold_product: Optional[str] = None  # Hacerlo opcional
    sales_by_customer: Dict[str, float]
    avg_purchase_per_customer: Dict[str, float]
    sales_by_category: Dict[str, float]
    profit_margin_products: List[ProfitMarginOut]
    sales_by_hour: Dict[int, float]
    orders_count: int

# ------------------ Endpoints de Ventas ------------------

@sales_router.post("/", response_model=SaleOut)
def create_sale_endpoint(
    sale_data: SaleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Guardamos el ID del usuario logueado en el pedido cuando se factura
    sale = create_sale(db, sale_data, user_id=current_user.id)
    return sale

@sales_router.get("/", response_model=List[SaleOut])
def get_all_sales_endpoint(db: Session = Depends(get_db)):
    return get_all_sales(db)

@sales_router.get("/{sale_id}", response_model=SaleOut)
def get_sale_by_id_endpoint(sale_id: int, db: Session = Depends(get_db)):
    sale = get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale

@sales_router.put("/{sale_id}", response_model=SaleOut)
def update_sale_endpoint(sale_id: int, sale_data: SaleCreate, db: Session = Depends(get_db)):
    return update_sale(db, sale_id, sale_data)

@sales_router.delete("/{sale_id}", response_model=SaleOut)
def delete_sale_endpoint(sale_id: int, db: Session = Depends(get_db)):
    return delete_sale(db, sale_id)

@sales_router.get("/day/", response_model=List[SaleOut])
def get_sales_for_day(day: date, db: Session = Depends(get_db)):
    sales = sales_for_day(db, day)
    return [SaleOut.model_validate(s) for s in sales]

@sales_router.get("/range/earnings/")
def get_earnings_by_date_range(
    start_date: date, 
    end_date: date, 
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400, 
            detail="La fecha de inicio no puede ser posterior a la fecha de fin"
        )
    return earnings_by_date_range(db, start_date, end_date)

# ------------------ Métricas por Día ------------------

@sales_router.get("/day/metrics/", response_model=SalesMetrics)
def get_sales_metrics_for_day(day: date, db: Session = Depends(get_db)):
    sales = sales_for_day(db, day)

    # Inicializar todas las métricas con valores por defecto
    metrics = {
        "total_sales": 0.0,
        "total_quantity": Decimal(0),
        "most_sold_product": None,
        "sales_by_customer": {},
        "avg_purchase_per_customer": {},
        "sales_by_category": {},
        "profit_margin_products": [],
        "sales_by_hour": {},
        "orders_count": 0
    }

    if not sales:  # Si no hay ventas, retornamos los valores por defecto
        return SalesMetrics(**metrics)

    product_sales: Dict[str, int] = {}  # Definir product_sales aquí

    # Procesar las ventas
    for sale in sales:
        metrics["total_sales"] += sale.total
        metrics["orders_count"] += 1
        hour = sale.date.hour
        metrics["sales_by_hour"][hour] = metrics["sales_by_hour"].get(hour, 0.0) + sale.total

        # Verificar si sale.order no es None antes de acceder a sus elementos
        if sale.order:
            for item in sale.order.items:
                name = item.product.name
                qty = item.quantity

                # Actualizar cantidad por producto
                product_sales[name] = product_sales.get(name, 0) + qty
                
                metrics["total_quantity"] += Decimal(str(qty))

                # Actualizar ventas por cliente
                cust = sale.order.customer.name
                metrics["sales_by_customer"][cust] = metrics["sales_by_customer"].get(cust, 0.0) + sale.total

                # Actualizar ventas por categoría
                cat = item.product.category.name
                metrics["sales_by_category"][cat] = metrics["sales_by_category"].get(cat, 0.0) + sale.total

                # Agregar margen de ganancia
                metrics["profit_margin_products"].append(ProfitMarginOut(
                    product_name=name,
                    margin=float(item.product.profit_percentage)
                ))

    # Calcular producto más vendido (solo si hay productos)
    if product_sales:
        metrics["most_sold_product"] = max(product_sales.items(), key=lambda x: x[1])[0]
    
    # Ordenar márgenes de ganancia
    metrics["profit_margin_products"].sort(key=lambda x: x.margin, reverse=True)

    # Calcular promedio por cliente
    for cust in metrics["sales_by_customer"]:
        customer_sales_count = len([
    s for s in sales if s.order and s.order.customer and s.order.customer.name == cust
])

        if customer_sales_count > 0:
            metrics["avg_purchase_per_customer"][cust] = metrics["sales_by_customer"][cust] / customer_sales_count

    return SalesMetrics(**metrics)

# ------------------ Rango de Fechas y Ganancias ------------------

@sales_router.get("/range/")
def get_sales_between_dates(start_date: date, end_date: date, db: Session = Depends(get_db)):
    return sales_between_dates(db, start_date, end_date)

@sales_router.get("/day/earnings/")
def get_earnings_per_day(day: date, db: Session = Depends(get_db)):
    return earnings_per_day(day, db)

# ------------------ Historial por Cliente ------------------

@sales_router.get("/history/{customer_id}", response_model=List[SaleOut])
def get_sales_history(customer_id: int, db: Session = Depends(get_db)):
    return get_sales_by_customer(db, customer_id)
