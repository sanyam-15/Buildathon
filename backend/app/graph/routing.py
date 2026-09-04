"""Routing functions for LangGraph conditional edges."""

from typing import Literal
from app.graph.state import RecoveryState


def route_to_specialist(
    state: RecoveryState,
) -> Literal[
    "failed_payment_specialist",
    "abandoned_cart_specialist",
    "subscription_specialist",
    "overdue_receivable_specialist",
    "escalate",
]:
    """Route to the appropriate specialist based on leakage category."""
    category = state.get("leakage_category", "UNKNOWN")

    if category == "FAILED_PAYMENT":
        return "failed_payment_specialist"
    elif category == "ABANDONED_CART":
        return "abandoned_cart_specialist"
    elif category == "SUBSCRIPTION_FAILURE":
        return "subscription_specialist"
    elif category == "OVERDUE_RECEIVABLE":
        return "overdue_receivable_specialist"
    else:
        # UNKNOWN or low confidence — escalate
        return "escalate"


def route_after_policy(
    state: RecoveryState,
) -> Literal["execution_agent", "replan", "escalate"]:
    """Route based on policy engine result."""
    policy_result = state.get("policy_result", {})
    approved = policy_result.get("approved", False)
    replan_count = state.get("replan_count", 0)

    if approved:
        return "execution_agent"

    # If blocked and we haven't exceeded replan limit, try replanning
    violations = policy_result.get("violations", [])
    if "MAX_REPLAN_ATTEMPTS_EXCEEDED" in violations:
        return "escalate"

    if replan_count < 2:
        return "replan"

    return "escalate"


def route_after_monitor(
    state: RecoveryState,
) -> Literal["end", "replan", "escalate"]:
    """Route based on monitor outcome."""
    status = state.get("status", "")
    monitor_status = state.get("monitor_status", "")

    if status == "RECOVERED" or monitor_status == "PAYMENT_SUCCESS":
        return "end"

    if status == "ESCALATED":
        return "escalate"

    if status == "FAILED":
        return "end"

    # WAITING_FOR_PAYMENT — end the graph (webhook will handle the rest)
    return "end"
