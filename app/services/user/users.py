from sqlalchemy.orm import Session
from app.models.users.users import User
from app.schemas.users.users import UserCreate
from sqlalchemy.future import select
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlalchemy.future import select
from app.core.security import get_password_hash

def update_user(db: Session, user_id: int, user_data, current_user):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permisos
    if current_user.rol != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    data = user_data.dict(exclude_unset=True)

    # Solo admin puede cambiar rol
    if "rol" in data and current_user.rol != "admin":
        del data["rol"]

    # Si viene password → hashearla
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))

    for key, value in data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user: User):
    # Solo admin puede eliminar
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios")

    # Evitar que el admin se borre a sí mismo
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(user)
    db.commit()

    return {"message": "Usuario eliminado correctamente"}


pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto")

def register_user(db: Session, user: UserCreate):
    hashed_password= pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        direction=user.direction,
        image=user.image,
        rol=user.rol or "user"  # Incluimos el campo rol, por defecto "user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def user_detail(db:Session,user_id:int):
    user = db.execute(select(User).where(User.id == user_id))
    return user.scalars().first()
