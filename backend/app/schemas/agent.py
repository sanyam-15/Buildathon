"""Pydantic schemas for agent structured outputs."""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class LeakageCategory(str, Enum):
    FAILED_PAYMENT = "FAILED_PAYMENT"
    ABANDONED_CART = "ABANDONED_CART"
    SUBSCRIPTION_FAILURE = "SUBSCRIPTION_FAILURE"
    OVERDUE_RECEIVABLE = "OVERDUE_RECEIVABLE"
    UNKNOWN = "UNKNOWN"


class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Revenue Sentinel output
class SentinelOutput(BaseModel):
    revenue_at_risk: bool = Field(description="Whether revenue is at risk")
    amount_at_risk: float = Field(description="Estimated amount at risk in the event currency")
    priority: PriorityLevel = Field(description="Priority level based on amount, urgency, and recoverability")
    reason: str = Field(description="Why this is a revenue risk event")
    urgency_score: float = Field(ge=0, le=1, description="Urgency score from 0 to 1")
    recovery_probability: float = Field(ge=0, le=1, description="Estimated probability of successful recovery")


# Leakage Classifier output
class ClassifierOutput(BaseModel):
    category: LeakageCategory = Field(description="The classified leakage category")
    confidence: float = Field(ge=0, le=1, description="Classification confidence")
    reason: str = Field(description="Why this category was chosen")
    signals_used: List[str] = Field(description="Which signals were used for classification")


# Specialist investigation output
class SpecialistOutput(BaseModel):
    customer_value: str = Field(description="Customer value tier: HIGH, MEDIUM, LOW")
    historical_payment_success_rate: float = Field(ge=0, le=1, description="Historical payment success rate")
    previous_recovery_attempts: int = Field(description="Number of previous recovery attempts")
    root_cause: str = Field(description="Root cause of revenue leakage")
    recovery_confidence: float = Field(ge=0, le=1, description="Confidence in recovery success")
    additional_context: str = Field(description="Any additional context about the situation")
    recommended_approach: str = Field(description="Recommended high-level approach")


# B2B invoice analyzer output
class InvoiceAnalyzerOutput(BaseModel):
    aging_bucket: str = Field(description="Aging bucket: CURRENT, 1_30, 31_60, 61_90, 90_PLUS")
    invoice_tier: str = Field(description="Invoice value tier: HIGH, MEDIUM, LOW")
    urgency: str = Field(description="Urgency: CRITICAL, HIGH, MEDIUM, LOW")
    findings: str = Field(description="Key invoice analysis findings")
    recommended_tone: str = Field(description="Recommended collections tone: soft, firm, formal, escalate")


# B2B history analyst output
class HistoryAnalystOutput(BaseModel):
    payer_reliability: str = Field(description="Payer reliability: EXCELLENT, GOOD, FAIR, POOR")
    historical_on_time_rate: float = Field(ge=0, le=1, description="Historical on-time payment rate")
    previous_followups: int = Field(description="Number of previous follow-up attempts")
    response_pattern: str = Field(description="Observed response pattern")
    risk_flags: List[str] = Field(description="Risk flags identified")
    findings: str = Field(description="Key payment history findings")


# B2B follow-up planner output
class FollowupPlannerOutput(BaseModel):
    recommended_action: str = Field(description="One of: REMIND, WAIT, ESCALATE, STOP, CREATE_PAYMENT_LINK")
    cooldown_hours: int = Field(description="Suggested hours to wait before next contact if WAIT")
    escalation_reason: Optional[str] = Field(default=None, description="Reason if escalating")
    stop_reason: Optional[str] = Field(default=None, description="Reason if stopping")
    confidence: float = Field(ge=0, le=1, description="Confidence in follow-up plan")
    reasoning: str = Field(description="Why this follow-up decision was chosen")


# Strategy alternative
class StrategyAlternative(BaseModel):
    action: str = Field(description="Action name")
    recovery_probability: float = Field(ge=0, le=1, description="Expected recovery probability")
    reasoning: str = Field(description="Why this probability")


class RecoveryAction(str, Enum):
    SMART_RETRY = "SMART_RETRY"
    WAIT = "WAIT"
    CREATE_PAYMENT_LINK = "CREATE_PAYMENT_LINK"
    SEND_EMAIL = "SEND_EMAIL"
    SEND_WHATSAPP = "SEND_WHATSAPP"
    OFFER_DISCOUNT = "OFFER_DISCOUNT"
    SEND_INVOICE_REMINDER = "SEND_INVOICE_REMINDER"
    SCHEDULE_FOLLOWUP = "SCHEDULE_FOLLOWUP"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    STOP = "STOP"


class CommunicationChannel(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    NONE = "NONE"


# Recovery Strategist output
class StrategistOutput(BaseModel):
    primary_action: RecoveryAction = Field(description="Primary recovery action")
    communication_channel: CommunicationChannel = Field(description="Communication channel to use")
    expected_recovery_probability: float = Field(ge=0, le=1, description="Expected probability of recovery")
    reason: str = Field(description="Why this strategy was selected")
    alternatives_considered: List[StrategyAlternative] = Field(description="Alternative strategies evaluated")
    discount_percent: Optional[float] = Field(default=None, description="Discount percentage if offering discount")
    email_subject: Optional[str] = Field(default=None, description="Suggested email subject")
    email_body: Optional[str] = Field(default=None, description="Suggested email body template")
    message_body: Optional[str] = Field(default=None, description="Suggested WhatsApp/SMS message")


# Execution Agent output
class ExecutionOutput(BaseModel):
    actions_taken: List[str] = Field(description="List of actions executed")
    payment_link_created: bool = Field(default=False)
    payment_link_url: Optional[str] = Field(default=None)
    communication_sent: bool = Field(default=False)
    communication_channel: Optional[str] = Field(default=None)
    retry_attempted: bool = Field(default=False)
    success: bool = Field(description="Whether execution was successful")
    details: str = Field(description="Execution details")


# Monitor output
class MonitorOutput(BaseModel):
    status: str = Field(description="Current monitoring status")
    payment_received: bool = Field(default=False)
    amount_recovered: float = Field(default=0.0)
    should_replan: bool = Field(default=False)
    reason: str = Field(description="Monitoring observation")
