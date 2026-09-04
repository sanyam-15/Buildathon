"""Deterministic Policy Engine — checks business rules without LLM involvement.

This is intentionally NOT LLM-based. It enforces hard business constraints
that the AI cannot override, demonstrating bounded autonomy.
"""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus

# ──────────────────────────────────────
# POLICY CONSTANTS (configurable)
# ──────────────────────────────────────
MAX_RETRY_ATTEMPTS = 3
MAX_MESSAGES_PER_DAY = 2
MAX_AUTO_RECOVERY_AMOUNT = 50000  # INR
MAX_AUTO_DISCOUNT_PERCENT = 10
MIN_RETRY_INTERVAL_MINUTES = 30
MAX_REPLAN_ATTEMPTS = 2


async def policy_engine(state: RecoveryState) -> dict:
    """Check strategy against deterministic policy rules."""
    case_id = state["case_id"]
    strategy = state.get("strategy", {})
    amount = state.get("amount_at_risk", 0)
    retry_count = state.get("retry_count", 0)
    replan_count = state.get("replan_count", 0)

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="policy_check",
        agent="policy_engine",
        message="Checking strategy against business policy guardrails",
    )

    violations = []
    primary_action = strategy.get("primary_action", "")

    # Rule 1: Retry limits
    if primary_action == "SMART_RETRY" and retry_count >= MAX_RETRY_ATTEMPTS:
        violations.append("MAX_RETRY_ATTEMPTS_EXCEEDED")

    # Rule 2: Amount limits
    if amount > MAX_AUTO_RECOVERY_AMOUNT and primary_action not in ("ESCALATE_TO_HUMAN", "STOP"):
        violations.append("MAX_AUTO_RECOVERY_AMOUNT_EXCEEDED")

    # Rule 3: Discount limits
    discount = strategy.get("discount_percent", 0)
    if discount and discount > MAX_AUTO_DISCOUNT_PERCENT:
        violations.append("MAX_AUTO_DISCOUNT_PERCENT_EXCEEDED")

    # Rule 4: Replan limits
    if replan_count >= MAX_REPLAN_ATTEMPTS and primary_action not in ("ESCALATE_TO_HUMAN", "STOP"):
        violations.append("MAX_REPLAN_ATTEMPTS_EXCEEDED")

    # Rule 5: Communication frequency (simplified — in production, check DB)
    comm_count = len(state.get("communication_results", []))
    if comm_count >= MAX_MESSAGES_PER_DAY and strategy.get("communication_channel") in ("EMAIL", "WHATSAPP"):
        violations.append("MAX_MESSAGES_PER_DAY_EXCEEDED")

    approved = len(violations) == 0

    if approved:
        reason = "Action falls within autonomous recovery limits."
    else:
        reason = f"Policy violations: {', '.join(violations)}"

    policy_result = {
        "approved": approved,
        "violations": violations,
        "reason": reason,
        "checks_performed": {
            "retry_count": retry_count,
            "max_retries": MAX_RETRY_ATTEMPTS,
            "amount": amount,
            "max_amount": MAX_AUTO_RECOVERY_AMOUNT,
            "replan_count": replan_count,
            "max_replans": MAX_REPLAN_ATTEMPTS,
            "communications_sent": comm_count,
            "max_messages": MAX_MESSAGES_PER_DAY,
        },
    }

    event_type = "policy_approved" if approved else "policy_blocked"
    emoji = "✓" if approved else "⚠"

    await event_bus.emit_simple(
        case_id=case_id,
        event_type=event_type,
        agent="policy_engine",
        message=f"{emoji} Policy {'APPROVED' if approved else 'BLOCKED'}: {reason}",
        metadata=policy_result,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="policy_engine",
        message=f"Policy check complete: {'Approved' if approved else 'Blocked'}",
        metadata=policy_result,
    )

    return {
        "policy_result": policy_result,
        "audit_trail": [{"agent": "policy_engine", "action": "policy_check", "result": policy_result}],
    }
