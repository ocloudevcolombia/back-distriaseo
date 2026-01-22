from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.store.products.categories import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category_by_id
)
from app.schemas.store.products.products import (
    CreateCategory,
    UpdateCategory,
    ResponseCategory
)

categories_router = APIRouter(prefix="/categories", tags=["Categories"])

@categories_router.get("/", response_model=List[ResponseCategory])
def get_all_categories_endpoint(db: Session = Depends(get_db)):
    """
    Obtiene todas las categorías.
    """
    return get_all_categories(db)

@categories_router.post("/", response_model=ResponseCategory)
def register_category(category: CreateCategory, db: Session = Depends(get_db)):
    return create_category(category, db)

@categories_router.get("/{category_id}", response_model=ResponseCategory)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@categories_router.patch("/{category_id}", response_model=ResponseCategory)
def patch_category(category_id: int, category_data: UpdateCategory, db: Session = Depends(get_db)):
    category = update_category(category_id, category_data, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@categories_router.delete("/{category_id}", response_model=ResponseCategory)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = delete_category_by_id(category_id, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
