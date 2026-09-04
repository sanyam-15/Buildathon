"""B2B History Analyst sub-agent — payment history and prior communication."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import HistoryAnalystOutput
from langchain_openai import ChatOpenAI
from app.config import settings


async def b2b_history_analyst(state: RecoveryState) -> dict:
    """Analyze buyer payment history and prior follow-up outcomes."""
    case_id = state["case_id"]
    investigation = dict(state.get("investigation") or {})
    raw_event = state.get("raw_event", {})
    signals = raw_event.get("signals", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="b2b_history_analyst",
        message="Analyzing payment history and prior follow-ups",
        metadata={"parent": "overdue_receivable_specialist", "sub_node": True},
    )

    previous_followups = investigation.get("previous_followups") or signals.get("previous_followups") or 0
    response_behavior = investigation.get("response_behavior") or signals.get("response_behavior") or "none"
    payment_history_score = signals.get("payment_history_score")
    customer_history = investigation.get("customer_history", {})

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.15,
    )
    structured_llm = llm.with_structured_output(HistoryAnalystOutput)

    prompt = f"""You are a B2B History Analyst sub-agent within the Overdue Receivable Specialist.

Review buyer payment behavior and prior collections attempts:

Investigation so far:
{investigation}

Signals:
- Previous follow-ups: {previous_followups}
- Response behavior: {response_behavior}
- Payment history score (if any): {payment_history_score}
- Customer history: {customer_history}

Determine:
1. payer_reliability: EXCELLENT | GOOD | FAIR | POOR
2. historical_on_time_rate (0-1)
3. previous_followups count
4. response_pattern summary (e.g. ignores reminders, promises then delays, disputes)
5. risk_flags list (e.g. chronic_late_payer, dispute_risk, high_value_exposure)
6. findings summary

Be specific and useful for collections planning.
"""

    result: HistoryAnalystOutput = await structured_llm.ainvoke(prompt)

    history_analysis = {
        "payer_reliability": result.payer_reliability,
        "historical_on_time_rate": result.historical_on_time_rate,
        "previous_followups": result.previous_followups,
        "response_pattern": result.response_pattern,
        "risk_flags": result.risk_flags,
        "findings": result.findings,
        "response_behavior": response_behavior,
    }

    investigation["history_analysis"] = history_analysis

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="b2b_history_analyst",
        message=(
            f"Reliability {result.payer_reliability} · "
            f"{result.previous_followups} prior follow-ups · "
            f"Pattern: {result.response_pattern}"
        ),
        metadata=history_analysis,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="b2b_history_analyst",
        message=f"History analysis complete: {result.findings}",
        metadata=history_analysis,
    )

    return {
        "investigation": investigation,
        "audit_trail": [{"agent": "b2b_history_analyst", "action": "history_analysis", "result": history_analysis}],
    }
