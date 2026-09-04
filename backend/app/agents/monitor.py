"""Monitor Agent — watches the outcome of recovery actions."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus


async def monitor_agent(state: RecoveryState) -> dict:
    """Monitor the outcome of recovery execution."""
    case_id = state["case_id"]
    payment_link = state.get("payment_link")
    monitor_status = state.get("monitor_status", "WAITING_FOR_PAYMENT")
    replan_count = state.get("replan_count", 0)

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="monitor_agent",
        message=f"Monitoring recovery outcome — status: {monitor_status}",
    )

    # Check if payment was already received (via webhook updating the state)
    if monitor_status == "PAYMENT_SUCCESS":
        amount = state.get("amount_at_risk", 0)

        await event_bus.emit_simple(
            case_id=case_id,
            event_type="payment_verified",
            agent="monitor_agent",
            message=f"Payment verified — ₹{amount:,.0f} recovered",
            metadata={"amount": amount},
        )

        await event_bus.emit_simple(
            case_id=case_id,
            event_type="revenue_recovered",
            agent="monitor_agent",
            message=f"💰 Revenue recovered: ₹{amount:,.0f}",
            metadata={"amount": amount},
        )

        await event_bus.emit_simple(
            case_id=case_id,
            event_type="case_completed",
            agent="monitor_agent",
            message="Recovery case completed successfully",
        )

        return {
            "status": "RECOVERED",
            "recovered_amount": amount,
            "monitor_status": "PAYMENT_SUCCESS",
            "audit_trail": [{"agent": "monitor_agent", "action": "payment_verified", "amount_recovered": amount}],
        }

    # Payment not yet received — case enters waiting state
    # The webhook will update the case when payment arrives
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="waiting_for_payment",
        agent="monitor_agent",
        message="Waiting for customer payment — payment link sent",
        metadata={
            "payment_link": payment_link,
            "replan_count": replan_count,
        },
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="monitor_agent",
        message="Monitor agent entering watch mode — awaiting payment webhook",
    )

    # Mark case as WAITING — the webhook handler will check for payment
    return {
        "status": "WAITING_FOR_PAYMENT",
        "monitor_status": "WAITING_FOR_PAYMENT",
        "audit_trail": [{"agent": "monitor_agent", "action": "waiting", "status": "WAITING_FOR_PAYMENT"}],
    }
