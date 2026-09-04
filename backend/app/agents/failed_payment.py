"""Failed Payment Specialist — investigates context for failed payment events."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import SpecialistOutput
from app.tools.payment_tools import get_customer_history
from langchain_openai import ChatOpenAI
from app.config import settings


async def failed_payment_specialist(state: RecoveryState) -> dict:
    """Investigate failed payment context to inform recovery strategy."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]
    customer = state.get("customer", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="failed_payment_specialist",
        message="Investigating failed payment context",
    )

    # Tool call: get customer history
    customer_email = customer.get("email", "unknown@example.com") if customer else "unknown@example.com"
    customer_history = await get_customer_history(customer_email, case_id)

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="failed_payment_specialist",
        message=f"Customer has {customer_history['total_orders']} previous orders, {customer_history['payment_success_rate']*100:.0f}% success rate",
        metadata=customer_history,
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(SpecialistOutput)

    signals = raw_event.get("signals", {})
    failure_reason = signals.get("failure_reason", "unknown")

    prompt = f"""You are a Failed Payment Specialist AI agent. Analyze the context of a failed payment and provide your investigation findings.

Failed Payment Event:
{raw_event}

Customer History:
{customer_history}

Failure Reason: {failure_reason}

Investigate:
1. What is the customer's value tier? (HIGH if >5 orders and >80% success, MEDIUM if >2 orders, LOW otherwise)
2. What is their historical payment success rate?
3. How many previous recovery attempts have been made? (assume 0 for new cases)
4. What is the root cause of failure? (e.g., temporary_payment_failure, card_expired, insufficient_funds, bank_decline)
5. How confident are you that recovery will succeed? (0-1)
6. What additional context is relevant?
7. What high-level approach do you recommend?

Be specific and data-driven in your analysis.
"""

    result: SpecialistOutput = await structured_llm.ainvoke(prompt)

    investigation = {
        "specialist": "failed_payment",
        "customer_value": result.customer_value,
        "historical_payment_success_rate": result.historical_payment_success_rate,
        "previous_recovery_attempts": result.previous_recovery_attempts,
        "root_cause": result.root_cause,
        "recovery_confidence": result.recovery_confidence,
        "additional_context": result.additional_context,
        "recommended_approach": result.recommended_approach,
        "customer_history": customer_history,
    }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="failed_payment_specialist",
        message=f"Investigation complete — Customer value: {result.customer_value}, Root cause: {result.root_cause}",
        metadata=investigation,
    )

    return {
        "investigation": investigation,
        "audit_trail": [{"agent": "failed_payment_specialist", "action": "investigation", "result": investigation}],
    }
