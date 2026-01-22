from sqlalchemy import Column,String,Integer,Boolean
from app.core.database import Base


class Customer(Base):

    __tablename__="customers"

    id= Column(Integer(),primary_key=True,index=True)
    name=Column(String(50),nullable=False,index=True)
    cc = Column(Integer(),nullable=False)
    alias = Column(String(50),nullable=True,index=True)
    avatar=Column(String(50),nullable=True,index=True)
    phone = Column(String(20), nullable=True)  # Cambiado a String
    direction = Column(String(255),nullable=True,index=True)

    #relations
