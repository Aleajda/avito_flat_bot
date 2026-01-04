from sqlalchemy import *
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AppState(Base):
    __tablename__ = "app_state"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

class Flat(Base):
    __tablename__ = "flats"

    id = Column(Integer, primary_key=True)
    avito_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, unique=True, nullable=False)

    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    district = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    flat_id = Column(Integer, ForeignKey("flats.id", ondelete="CASCADE"))
    old_price = Column(Integer, nullable=False)
    new_price = Column(Integer, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
