"""Customer model."""

from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    lifetime_value = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
