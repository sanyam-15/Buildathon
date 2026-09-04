"""Abandoned Cart Specialist — investigates context for cart abandonment events."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import SpecialistOutput
from app.tools.payment_tools import get_customer_history
from langchain_openai import ChatOpenAI
from app.config import settings


async def abandoned_cart_specialist(state: RecoveryState) -> dict:
    """Investigate abandoned cart context to inform recovery strategy."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]
    customer = state.get("customer", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="abandoned_cart_specialist",
        message="Investigating abandoned cart context",
    )

    # Tool call: get customer history
    customer_email = customer.get("email", "unknown@example.com") if customer else "unknown@example.com"
    customer_history = await get_customer_history(customer_email, case_id)

    signals = raw_event.get("signals", {})
    inactive_minutes = signals.get("inactive_minutes", 0)
    cart_items = raw_event.get("cart_items", [])
    amount = raw_event.get("amount", 0)

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="abandoned_cart_specialist",
        message=f"Cart value: ₹{amount:,.0f}, Inactive for {inactive_minutes} minutes, {len(cart_items)} items",
        metadata={"cart_value": amount, "inactive_minutes": inactive_minutes, "items_count": len(cart_items)},
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(SpecialistOutput)

    prompt = f"""You are an Abandoned Cart Specialist AI agent. Analyze the context of an abandoned cart and provide your investigation findings.

Abandoned Cart Event:
{raw_event}

Customer History:
{customer_history}

Cart Details:
- Cart value: ₹{amount:,.0f}
- Items in cart: {len(cart_items)}
- Checkout started: {signals.get('checkout_started', False)}
- Payment attempted: {signals.get('payment_attempted', False)}
- Inactive minutes: {inactive_minutes}

Investigate:
1. What is the customer's value tier? (HIGH if loyal returning customer, MEDIUM if some history, LOW if new/unknown)
2. What is their historical purchase success rate?
3. How many previous recovery attempts have been made? (assume 0 for new cases)
4. What is the likely root cause of abandonment? (e.g., price_hesitation, checkout_friction, distraction, comparison_shopping)
5. How confident are you that recovery will succeed? (0-1) — Higher for recent, high-value customers
6. What additional context is relevant?
7. What high-level approach do you recommend?

Be specific and data-driven.
"""

    result: SpecialistOutput = await structured_llm.ainvoke(prompt)

    investigation = {
        "specialist": "abandoned_cart",
        "customer_value": result.customer_value,
        "historical_payment_success_rate": result.historical_payment_success_rate,
        "previous_recovery_attempts": result.previous_recovery_attempts,
        "root_cause": result.root_cause,
        "recovery_confidence": result.recovery_confidence,
        "additional_context": result.additional_context,
        "recommended_approach": result.recommended_approach,
        "customer_history": customer_history,
        "inactive_minutes": inactive_minutes,
    }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="abandoned_cart_specialist",
        message=f"Investigation complete — Customer value: {result.customer_value}, Root cause: {result.root_cause}",
        metadata=investigation,
    )

    return {
        "investigation": investigation,
        "audit_trail": [{"agent": "abandoned_cart_specialist", "action": "investigation", "result": investigation}],
    }
