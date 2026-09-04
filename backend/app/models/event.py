"""Revenue event model."""

from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class RevenueEvent(Base):
    __tablename__ = "revenue_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String, default="default_merchant")
    event_type = Column(String, nullable=True)  # determined by AI
    raw_payload = Column(JSON, nullable=False)
    amount_at_risk = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
