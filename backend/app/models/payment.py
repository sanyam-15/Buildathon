"""Payment and PaymentLink models."""

from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="pending")  # pending, paid, failed
    failure_reason = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class PaymentLink(Base):
    __tablename__ = "payment_links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recovery_case_id = Column(String, nullable=False, index=True)
    provider = Column(String, default="mock")  # mock, razorpay
    provider_link_id = Column(String, nullable=True)
    url = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="created")  # created, paid, expired
    description = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)
