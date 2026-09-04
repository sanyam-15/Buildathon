"""Pydantic schemas for API input events."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class CustomerInput(BaseModel):
    name: str = "Customer"
    email: str = "customer@example.com"
    phone: Optional[str] = None


class CartItem(BaseModel):
    name: str = "Product"
    quantity: int = 1
    price: float = 0.0


class SignalsInput(BaseModel):
    payment_attempted: Optional[bool] = None
    payment_status: Optional[str] = None  # failed, success, none
    failure_reason: Optional[str] = None
    checkout_started: Optional[bool] = None
    cart_created: Optional[bool] = None
    inactive_minutes: Optional[int] = None
    renewal_attempted: Optional[bool] = None
    renewal_status: Optional[str] = None


class RecoveryEventInput(BaseModel):
    """Input for triggering a recovery event. Category is NOT specified — AI determines it."""
    customer: CustomerInput
    amount: float = Field(gt=0, description="Amount in INR")
    currency: str = "INR"
    product_name: Optional[str] = "Product"
    merchant_name: Optional[str] = "RecoverAI Merchant"
    signals: SignalsInput
    cart_items: Optional[List[CartItem]] = None
    subscription_id: Optional[str] = None


class BatchRecoveryInput(BaseModel):
    """Input for batch recovery — auto-generates mixed events or accepts a list."""
    count: Optional[int] = 10
    events: Optional[List[RecoveryEventInput]] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
