"""LangGraph state definition for the recovery workflow.

This TypedDict defines the global state that flows through all agent nodes.
Each node reads from and writes to this state progressively.
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated
from operator import add


def merge_list(left: list, right: list) -> list:
    """Merge two lists by appending right to left."""
    return left + right


class RecoveryState(TypedDict):
    """Global state for the recovery workflow graph."""

    # Case identification
    case_id: str
    event_id: str

    # Raw input event
    raw_event: dict

    # Extracted entities
    customer: Optional[dict]
    transaction: Optional[dict]
    cart: Optional[dict]
    subscription: Optional[dict]
    invoice: Optional[dict]
    segment: Optional[str]  # B2C | B2B

    # Revenue Sentinel output
    revenue_risk: Optional[dict]

    # Leakage Classifier output
    leakage_category: Optional[str]
    classification_confidence: Optional[float]
    classification_reason: Optional[str]

    # Specialist investigation output
    investigation: Optional[dict]

    # Recovery Strategist output
    strategy: Optional[dict]

    # Policy Engine output
    policy_result: Optional[dict]

    # Execution results
    execution_results: Annotated[list, merge_list]
    payment_link: Optional[dict]
    communication_results: Annotated[list, merge_list]

    # Monitor state
    monitor_status: Optional[str]

    # Counters
    retry_count: int
    replan_count: int

    # Final status
    status: str  # CREATED, PROCESSING, RECOVERED, FAILED, ESCALATED

    # Revenue tracking
    amount_at_risk: float
    recovered_amount: float

    # Audit trail
    audit_trail: Annotated[list, merge_list]

    # Error tracking
    error: Optional[str]
