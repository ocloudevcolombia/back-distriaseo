from sqlalchemy import Column,String,Integer,Boolean,DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):

    __tablename__ ="users"

    id= Column(Integer(),primary_key=True,index=True)
    email= Column(String(255),unique=True,index=True,nullable=False)
    hashed_password = Column(String(255),nullable=False)
    full_name = Column(String(255),nullable=False,index=True)
    phone=Column(String(10),nullable=True)
    direction= Column(String(255))
    image = Column(String(255), nullable=True)
    is_active = Column(Boolean(),default=True)
    is_admin= Column(Boolean(),default=False)
    rol = Column(String(50), nullable=True, default="user")  # Campo para validar tipo de usuario
    create_at= Column(DateTime(timezone=True),server_default=func.now())