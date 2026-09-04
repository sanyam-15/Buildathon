"""Subscription Specialist — investigates context for subscription failure events."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import SpecialistOutput
from app.tools.payment_tools import get_customer_history
from langchain_openai import ChatOpenAI
from app.config import settings


async def subscription_specialist(state: RecoveryState) -> dict:
    """Investigate subscription failure context to inform recovery strategy."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]
    customer = state.get("customer", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="subscription_specialist",
        message="Investigating subscription failure context",
    )

    customer_email = customer.get("email", "unknown@example.com") if customer else "unknown@example.com"
    customer_history = await get_customer_history(customer_email, case_id)

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(SpecialistOutput)

    prompt = f"""You are a Subscription Specialist AI agent. Analyze the context of a subscription renewal failure.

Subscription Event:
{raw_event}

Customer History:
{customer_history}

Investigate:
1. What is the customer's value tier?
2. What is their historical payment success rate?
3. Previous recovery attempts (assume 0)?
4. Root cause (e.g., card_expired, insufficient_funds, cancelled_subscription)?
5. Recovery confidence (0-1)?
6. Additional context?
7. Recommended approach?
"""

    result: SpecialistOutput = await structured_llm.ainvoke(prompt)

    investigation = {
        "specialist": "subscription",
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
        agent="subscription_specialist",
        message=f"Investigation complete — Customer value: {result.customer_value}, Root cause: {result.root_cause}",
        metadata=investigation,
    )

    return {
        "investigation": investigation,
        "audit_trail": [{"agent": "subscription_specialist", "action": "investigation", "result": investigation}],
    }
