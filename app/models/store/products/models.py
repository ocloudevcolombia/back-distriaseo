from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import Enum
import enum


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer(), primary_key=True, nullable=False, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text(), nullable=True)


class UnidadMedidaEnum(enum.Enum):
    paquete="paquete"
    x15="x15"
    x30="x30"
    und = "und"
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    state = Column(Boolean(), default=True)
    purchase_price = Column(Float(), nullable=True)
    stock = Column(Numeric(10, 2), nullable=True, default=0)    
    sale_price = Column(Float(), nullable=True)
    profit_percentage = Column(Numeric(5,2), nullable=True, default=30.00)
    image_url = Column(String(255), nullable=True)  # 🖼 Aquí se guarda la URL de la imagen
    category_id = Column(Integer(), ForeignKey("categories.id"))

    # Relación
    category = relationship("Category", backref="products")
    unit = Column(Enum(UnidadMedidaEnum), nullable=False, default=UnidadMedidaEnum.und)
