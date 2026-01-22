from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.users.users import UserRead, UserCreate, UserUpdate
from app.services.user.users import register_user, user_detail, delete_user, update_user
from app.core.security import get_current_active_user,get_password_hash
from typing import List

from app.models.users.users import User

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/", response_model=UserRead)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_full_name = db.query(User).filter(User.full_name == user.full_name).first()
    if db_user_full_name:
        raise HTTPException(status_code=400, detail="Full name already registered")

    return register_user(db, user)


# ENDPOINT DE ROLES ELIMINADO - No existe tabla roles en BD

@user_router.delete("/{user_id}")
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return delete_user(db, user_id, current_user)


@user_router.get("/", response_model=List[UserRead])
def get_all_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    return db.query(User).offset(skip).limit(limit).all()


@user_router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@user_router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Solo permitir a admins o al propio usuario ver su información
    if current_user.rol != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Not enough permissions"
        )
    
    user = user_detail(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.put("/{user_id}", response_model=UserRead)
def update_user_route(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return update_user(db, user_id, user_data, current_user)
