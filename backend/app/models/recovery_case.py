"""Recovery case model — the central entity tracking each recovery workflow."""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, nullable=False)
    customer_id = Column(String, nullable=True)

    category = Column(String, nullable=True)  # FAILED_PAYMENT, ABANDONED_CART, OVERDUE_RECEIVABLE, etc.
    segment = Column(String, nullable=True)  # B2C | B2B
    classification_confidence = Column(Float, nullable=True)

    amount_at_risk = Column(Float, default=0.0)
    recovery_probability = Column(Float, nullable=True)

    status = Column(String, default="CREATED")  # CREATED, PROCESSING, RECOVERED, FAILED, ESCALATED

    selected_strategy = Column(JSON, nullable=True)
    strategy_reasoning = Column(JSON, nullable=True)

    recovered_amount = Column(Float, default=0.0)

    retry_count = Column(Integer, default=0)
    replan_count = Column(Integer, default=0)

    investigation = Column(JSON, nullable=True)
    policy_result = Column(JSON, nullable=True)
    execution_results = Column(JSON, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
