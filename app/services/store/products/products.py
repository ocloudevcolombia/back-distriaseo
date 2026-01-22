from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.schemas.store.products.products import UpdateProduct, CreateProduct
from app.models.store.products.models import Product
from decimal import Decimal



def create_product(product: CreateProduct, db: Session):
    """
    Crea un nuevo producto en la base de datos.
    Calcula automáticamente sale_price o profit_percentage si falta alguno.
    """
    purchase_price = product.purchase_price
    sale_price = product.sale_price
    profit_percentage = product.profit_percentage
    stock = product.stock if hasattr(product, 'stock') else 0  # Manejo seguro del stock

    if (sale_price is None or sale_price == 0) and profit_percentage is not None:
        sale_price = round(purchase_price * (1 + profit_percentage / 100), 2)
    elif (profit_percentage is None or profit_percentage == 0) and sale_price is not None:
        if purchase_price == 0:
            profit_percentage = 0
        else:
            profit_percentage = round(((sale_price / purchase_price) - 1) * 100, 2)

    new_product = Product(
        name=product.name,
        state=product.state,
        purchase_price=purchase_price,
        sale_price=sale_price,
        stock=stock,  # Añadido el campo stock
        profit_percentage=profit_percentage,
        category_id=product.category_id,
        image_url=product.image_url,
        unit=product.unit
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def add_to_stock(db: Session, product_id: int, quantity: float):
    """Suma cantidad al stock actual"""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Convertir float a Decimal
    quantity_decimal = Decimal(str(quantity))
    product.stock = (product.stock or Decimal('0')) + quantity_decimal
    db.commit()
    db.refresh(product)
    return product

def remove_from_stock(db: Session, product_id: int, quantity: float, allow_negative: bool = False):
    """Resta cantidad al stock actual"""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Convertir float a Decimal
    quantity_decimal = Decimal(str(quantity))
    current_stock = product.stock or Decimal('0')
    
    if not allow_negative and current_stock < quantity_decimal:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    
    product.stock = current_stock - quantity_decimal
    db.commit()
    db.refresh(product)
    return product

def get_all_products(db: Session):
    """
    Obtiene todos los productos de la base de datos.
    """
    return db.query(Product).all()


def get_product_by_id(product_id: int, db: Session):
    """
    Obtiene un producto por su ID.
    """
    product = db.execute(select(Product).where(Product.id == product_id))
    return product.scalars().first()


def patch_product(product_id: int, product_data: UpdateProduct, db: Session):
    """
    Actualiza un producto parcialmente.
    Calcula automáticamente sale_price o profit_percentage si falta alguno.
    """
    product = db.get(Product, product_id)
    if not product:
        return None

    # Solo actualiza campos que han sido enviados en la petición
    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    # Validación: si alguno de los campos clave es None, evitamos cálculos peligrosos
    purchase_price = product.purchase_price or 0
    sale_price = product.sale_price
    profit_percentage = product.profit_percentage

    # Recalcula si uno de los dos no está definido
    if (sale_price is None or sale_price == 0) and profit_percentage is not None:
        product.sale_price = round(purchase_price * (1 + profit_percentage / 100), 2)
    elif (profit_percentage is None or profit_percentage == 0) and sale_price is not None:
        product.profit_percentage = round(((sale_price / purchase_price) - 1) * 100, 2) if purchase_price != 0 else 0

    db.commit()
    db.refresh(product)
    return product




def delete_product_by_id(product_id: int, db: Session):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not Found")
    db.delete(product)
    db.commit()
    return product

