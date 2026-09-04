"""Pydantic schemas for recovery case responses."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class RecoveryCaseResponse(BaseModel):
    id: str
    event_id: str
    customer_id: Optional[str] = None
    category: Optional[str] = None
    classification_confidence: Optional[float] = None
    amount_at_risk: float = 0.0
    recovery_probability: Optional[float] = None
    status: str = "CREATED"
    selected_strategy: Optional[Dict[str, Any]] = None
    strategy_reasoning: Optional[Dict[str, Any]] = None
    recovered_amount: float = 0.0
    retry_count: int = 0
    replan_count: int = 0
    investigation: Optional[Dict[str, Any]] = None
    policy_result: Optional[Dict[str, Any]] = None
    # execution_results: Optional[Dict[str, Any]] = None
    execution_results: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_cases: int = 0
    total_at_risk: float = 0.0
    total_recovered: float = 0.0
    recovery_rate: float = 0.0
    active_cases: int = 0
    recovered_cases: int = 0
    failed_cases: int = 0
    escalated_cases: int = 0
    payment_links_generated: int = 0
    emails_sent: int = 0
    retries_attempted: int = 0


class BatchResult(BaseModel):
    total_events: int = 0
    revenue_at_risk: float = 0.0
    revenue_recovered: float = 0.0
    recovery_rate: float = 0.0
    successful_cases: int = 0
    failed_cases: int = 0
    escalated_cases: int = 0
    payment_links_generated: int = 0
    emails_sent: int = 0
    case_ids: List[str] = []
