from sqlalchemy import Column, String, Numeric,Integer
from app.core.database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # Nombre del servicio
    image_url = Column(String(255), nullable=True)         # URL de la imagen (opcional)
    price = Column(Numeric(10, 2), nullable=False)         # Precio con 2 decimales