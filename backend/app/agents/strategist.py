"""Recovery Strategist Agent — evaluates multiple strategies and selects the optimal one."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import StrategistOutput
from langchain_openai import ChatOpenAI
from app.config import settings


async def recovery_strategist(state: RecoveryState) -> dict:
    """Evaluate recovery strategies and select the best one."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]
    investigation = state.get("investigation", {})
    leakage_category = state.get("leakage_category", "UNKNOWN")
    amount = state.get("amount_at_risk", 0)
    customer = state.get("customer", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="recovery_strategist",
        message="Evaluating recovery strategies",
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.3,
    )
    structured_llm = llm.with_structured_output(StrategistOutput)

    customer_name = customer.get("name", "Customer") if customer else "Customer"
    customer_email = customer.get("email", "") if customer else ""
    replan_count = state.get("replan_count", 0)

    prompt = f"""You are a Recovery Strategist AI agent. Your goal is to select the BEST recovery action that maximizes expected recovered revenue while minimizing customer annoyance.

CONTEXT:
- Leakage Category: {leakage_category}
- Amount at Risk: ₹{amount:,.0f}
- Customer Name: {customer_name}
- Customer Email: {customer_email}
- Replan Attempt: {replan_count} (previous strategies may have failed)

INVESTIGATION FINDINGS:
{investigation}

AVAILABLE ACTIONS:
1. SMART_RETRY — Automatically retry the payment (best for temporary failures)
2. WAIT — Wait for customer to return (low effort, low probability)
3. CREATE_PAYMENT_LINK — Generate a hosted payment link (reduces checkout friction)
4. SEND_EMAIL — Send a recovery email reminder
5. SEND_WHATSAPP — Send WhatsApp message (if available)
6. OFFER_DISCOUNT — Offer a small discount to incentivize (max 10%)
7. ESCALATE_TO_HUMAN — Hand off to human agent
8. STOP — Do not attempt recovery

COMMUNICATION CHANNELS: EMAIL, WHATSAPP, SMS, NONE

RULES:
- You MUST evaluate at least 3 alternatives and provide recovery probabilities for each
- For FAILED_PAYMENT with temporary reasons → prefer SMART_RETRY or CREATE_PAYMENT_LINK
- For ABANDONED_CART → prefer CREATE_PAYMENT_LINK + EMAIL
- For high-value customers → prefer gentler approaches
- For replan attempts > 0 → try a DIFFERENT strategy than before
- If replan_count >= 2 → consider ESCALATE_TO_HUMAN or STOP
- CREATE_PAYMENT_LINK almost always requires a communication channel to deliver it (EMAIL or WHATSAPP)
- Generate a professional, personalized email subject and body if EMAIL is chosen
- The email body should mention the customer name, amount, and include a placeholder {{payment_link}} for the actual link

Select the optimal strategy. Explain your reasoning clearly.
"""

    result: StrategistOutput = await structured_llm.ainvoke(prompt)

    # Emit each alternative considered
    for alt in result.alternatives_considered:
        await event_bus.emit_simple(
            case_id=case_id,
            event_type="strategy_evaluated",
            agent="recovery_strategist",
            message=f"→ {alt.action}: {alt.recovery_probability*100:.0f}% expected recovery — {alt.reasoning}",
            metadata={"action": alt.action, "probability": alt.recovery_probability, "reasoning": alt.reasoning},
        )

    strategy_data = {
        "primary_action": result.primary_action.value,
        "communication_channel": result.communication_channel.value,
        "expected_recovery_probability": result.expected_recovery_probability,
        "reason": result.reason,
        "alternatives_considered": [
            {"action": a.action, "recovery_probability": a.recovery_probability, "reasoning": a.reasoning}
            for a in result.alternatives_considered
        ],
        "discount_percent": result.discount_percent,
        "email_subject": result.email_subject,
        "email_body": result.email_body,
        "message_body": result.message_body,
    }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="decision_made",
        agent="recovery_strategist",
        message=f"Selected: {result.primary_action.value} via {result.communication_channel.value} — {result.expected_recovery_probability*100:.0f}% expected recovery",
        metadata=strategy_data,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="recovery_strategist",
        message=f"Strategy selected: {result.reason}",
        metadata=strategy_data,
    )

    return {
        "strategy": strategy_data,
        "audit_trail": [{"agent": "recovery_strategist", "action": "strategy_selection", "result": strategy_data}],
    }
