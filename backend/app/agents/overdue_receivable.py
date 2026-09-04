"""Overdue Receivable Specialist — B2B entry node for receivables recovery.

Investigates overdue invoice context, then hands off to B2B sub-agents
(invoice analyzer → history analyst → follow-up planner).
"""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import SpecialistOutput
from app.tools.payment_tools import get_customer_history
from langchain_openai import ChatOpenAI
from app.config import settings


async def overdue_receivable_specialist(state: RecoveryState) -> dict:
    """Investigate overdue B2B receivable context to seed sub-agent analysis."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]
    customer = state.get("customer", {})
    invoice = state.get("invoice") or raw_event.get("invoice") or {}

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="overdue_receivable_specialist",
        message="Investigating overdue B2B receivable",
        metadata={"segment": "B2B", "invoice_id": invoice.get("invoice_id")},
    )

    customer_email = customer.get("email", "unknown@example.com") if customer else "unknown@example.com"
    customer_history = await get_customer_history(customer_email, case_id)

    signals = raw_event.get("signals", {})
    days_overdue = signals.get("days_overdue") or invoice.get("days_overdue") or 0
    previous_followups = signals.get("previous_followups") or 0
    response_behavior = signals.get("response_behavior") or "none"
    company = invoice.get("company_name") or customer.get("name", "Unknown Company")

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="overdue_receivable_specialist",
        message=(
            f"Invoice {invoice.get('invoice_id', 'N/A')} for {company} — "
            f"{days_overdue}d overdue, {previous_followups} prior follow-ups, "
            f"response: {response_behavior}"
        ),
        metadata={
            "days_overdue": days_overdue,
            "previous_followups": previous_followups,
            "response_behavior": response_behavior,
            "customer_history": customer_history,
        },
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(SpecialistOutput)

    prompt = f"""You are an Overdue Receivable Specialist for B2B collections.
Analyze this overdue invoice and provide investigation findings.

Invoice / Receivable Event:
{raw_event}

Invoice Details:
{invoice}

Customer / Buyer History:
{customer_history}

Signals:
- Days overdue: {days_overdue}
- Previous follow-ups: {previous_followups}
- Response behavior: {response_behavior}

Investigate:
1. Buyer value tier (HIGH if large invoice + good history, etc.)
2. Historical payment success rate
3. Previous recovery / follow-up attempts
4. Root cause (cash_flow_delay, disputed_invoice, ignored_reminders, process_delay, etc.)
5. Recovery confidence (0-1)
6. Additional context
7. Recommended high-level approach (remind, wait, escalate, or stop)

Be specific and data-driven.
"""

    result: SpecialistOutput = await structured_llm.ainvoke(prompt)

    investigation = {
        "specialist": "overdue_receivable",
        "segment": "B2B",
        "customer_value": result.customer_value,
        "historical_payment_success_rate": result.historical_payment_success_rate,
        "previous_recovery_attempts": result.previous_recovery_attempts,
        "root_cause": result.root_cause,
        "recovery_confidence": result.recovery_confidence,
        "additional_context": result.additional_context,
        "recommended_approach": result.recommended_approach,
        "customer_history": customer_history,
        "invoice": invoice,
        "days_overdue": days_overdue,
        "previous_followups": previous_followups,
        "response_behavior": response_behavior,
    }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="overdue_receivable_specialist",
        message=(
            f"B2B investigation seeded — Buyer: {result.customer_value}, "
            f"Root cause: {result.root_cause}"
        ),
        metadata=investigation,
    )

    return {
        "segment": "B2B",
        "invoice": invoice,
        "investigation": investigation,
        "audit_trail": [{"agent": "overdue_receivable_specialist", "action": "investigation", "result": investigation}],
    }
