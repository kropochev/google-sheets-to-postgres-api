from sqlalchemy import Column, Integer, Date, DECIMAL, Boolean

from database import Base


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, index=True)
    price_usd = Column(DECIMAL)
    delivery_time = Column(Date)
    price_rub = Column(DECIMAL)
    notify = Column(Boolean, default=False)
