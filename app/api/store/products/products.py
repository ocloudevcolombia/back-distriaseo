from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
import os
from app.models.store.products.models import Product
from app.core.database import get_db
from app.services.store.products.products import create_product, get_product_by_id, delete_product_by_id, add_to_stock,remove_from_stock,patch_product, get_all_products
from app.schemas.store.products.products import CreateProduct, ResponseProduct, UpdateProduct, ProductOut

products_router = APIRouter(prefix="/products", tags=["Products"])

# Ruta para obtener todos los productos
@products_router.get("/", response_model=List[ProductOut])
def get_all_products_endpoint(db: Session = Depends(get_db)):
    """
    Obtiene todos los productos.
    """
    products = get_all_products(db)
    return products

@products_router.post("/", response_model=ResponseProduct)
async def register_product(product: CreateProduct, db: Session = Depends(get_db)):

    new_product = create_product(product, db)  # Llamamos al servicio
    return new_product

@products_router.post("/{product_id}/add-stock", response_model=ResponseProduct)
def add_stock_endpoint(
    product_id: int,
    quantity: float,  # Cantidad positiva a sumar
    db: Session = Depends(get_db)
):
    return add_to_stock(db, product_id, quantity)

@products_router.post("/{product_id}/remove-stock", response_model=ResponseProduct)
def remove_stock_endpoint(
    product_id: int,
    quantity: float,  # Cantidad positiva a restar
    allow_negative: bool = False,  # Permite stock negativo si es True
    db: Session = Depends(get_db)
):
    return remove_from_stock(db, product_id, quantity, allow_negative)

# Ruta para obtener un producto específico
@products_router.get("/{product_id}", response_model=ResponseProduct)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto por su ID.
    """
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not Found")
    return product

# Ruta para actualizar un producto
@products_router.patch("/{product_id}", response_model=ResponseProduct)
def update_product(product_id: int, product_data: UpdateProduct, db: Session = Depends(get_db)):
    """
    Actualiza un producto existente.
    """
    product = patch_product(product_id, product_data, db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not Found")
    return product

# Ruta para eliminar un producto
@products_router.delete("/{product_id}", response_model=ResponseProduct)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = delete_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not Found")
    return product
