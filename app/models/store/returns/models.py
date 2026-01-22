from sqlalchemy import Column, Integer, Numeric, DateTime
from datetime import datetime
import pytz
from app.core.database import Base

class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    amount_returned = Column(Numeric(10, 2), nullable=False)  # Cantidad de dinero devuelto
    return_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))  # Fecha de la devolución ajustada a Colombia

    def __repr__(self):
        return f"<Return id={self.id} amount_returned={self.amount_returned} return_date={self.return_date}>"
