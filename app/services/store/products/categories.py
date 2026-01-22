from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.store.products.models import Category
from app.schemas.store.products.products import CreateCategory, UpdateCategory

def create_category(category: CreateCategory, db: Session):
    new_category = Category(
        name=category.name,
        description=category.description
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def get_all_categories(db: Session):
    categories = db.query(Category).all()
    return categories

def get_category_by_id(category_id: int, db: Session):
    result = db.execute(select(Category).where(Category.id == category_id))
    return result.scalars().first()

def update_category(category_id: int, category_data: UpdateCategory, db: Session):
    category = db.get(Category, category_id)
    if not category:
        return None
    
    for key, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

def delete_category_by_id(category_id: int, db: Session):
    category = db.get(Category, category_id)
    if not category:
        return None
    
    db.delete(category)
    db.commit()
    return category
