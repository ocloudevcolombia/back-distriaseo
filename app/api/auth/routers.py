from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated

from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    invalidate_token,
    oauth2_scheme  # Esta es la importación que faltaba
)
from app.schemas.users.auth import (
    Token,
    UserLogin,
    PasswordResetRequest,
    PasswordReset
)
from app.models.users.users import User
from app.core.config import settings
from app.services.auth.services import (
    generate_password_reset_token,
    verify_password_reset_token
)
from app.services.auth.email import send_reset_password_email

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.full_name, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.full_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    token: str = Depends(oauth2_scheme)
):
    # Invalida el token actual
    invalidate_token(token)
    return {"message": "Successfully logged out"}

@auth_router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
async def recover_password(
    password_recovery: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == password_recovery.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    
    password_reset_token = generate_password_reset_token(email=user.email)
    await send_reset_password_email(
        email_to=user.email,
        token=password_reset_token,
        background_tasks=background_tasks
    )
    return {"message": "Password recovery email sent"}

@auth_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: PasswordReset,
    db: Session = Depends(get_db)
):
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    
    hashed_password = get_password_hash(body.new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"message": "Password updated successfully"}