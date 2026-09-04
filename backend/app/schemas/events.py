"""Pydantic schemas for API input events."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class SegmentType(str, Enum):
    B2C = "B2C"
    B2B = "B2B"


class CustomerInput(BaseModel):
    name: str = "Customer"
    email: str = "customer@example.com"
    phone: Optional[str] = None


class CartItem(BaseModel):
    name: str = "Product"
    quantity: int = 1
    price: float = 0.0


class InvoiceInput(BaseModel):
    """B2B invoice / receivable context."""
    invoice_id: str = "INV-1001"
    company_name: str = "Acme Corp"
    po_number: Optional[str] = None
    due_date: Optional[str] = None
    days_overdue: int = 15
    invoice_value: Optional[float] = None


class SignalsInput(BaseModel):
    payment_attempted: Optional[bool] = None
    payment_status: Optional[str] = None  # failed, success, none
    failure_reason: Optional[str] = None
    checkout_started: Optional[bool] = None
    cart_created: Optional[bool] = None
    inactive_minutes: Optional[int] = None
    renewal_attempted: Optional[bool] = None
    renewal_status: Optional[str] = None
    # B2B receivable signals
    invoice_overdue: Optional[bool] = None
    days_overdue: Optional[int] = None
    previous_followups: Optional[int] = None
    response_behavior: Optional[str] = None  # none, acknowledged, promised_payment, disputed, ignored
    payment_history_score: Optional[float] = None  # 0-1


class RecoveryEventInput(BaseModel):
    """Input for triggering a recovery event. Category is NOT specified — AI determines it."""
    customer: CustomerInput
    amount: float = Field(gt=0, description="Amount in INR")
    currency: str = "INR"
    product_name: Optional[str] = "Product"
    merchant_name: Optional[str] = "RecoverAI Merchant"
    segment: SegmentType = SegmentType.B2C
    signals: SignalsInput
    cart_items: Optional[List[CartItem]] = None
    subscription_id: Optional[str] = None
    invoice: Optional[InvoiceInput] = None


class BatchRecoveryInput(BaseModel):
    """Input for batch recovery — auto-generates mixed events or accepts a list."""
    count: Optional[int] = 10
    events: Optional[List[RecoveryEventInput]] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    segment: Optional[SegmentType] = None  # None = mixed B2C+B2B
