"""B2B History Analyst sub-agent — payment history and prior communication."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import HistoryAnalystOutput
from app.tools.payment_tools import get_buyer_payment_score
from langchain_openai import ChatOpenAI
from app.config import settings


async def b2b_history_analyst(state: RecoveryState) -> dict:
    """Analyze buyer payment history and prior follow-up outcomes."""
    case_id = state["case_id"]
    investigation = dict(state.get("investigation") or {})
    raw_event = state.get("raw_event", {})
    signals = raw_event.get("signals", {})
    customer = state.get("customer") or raw_event.get("customer") or {}
    invoice = state.get("invoice") or investigation.get("invoice") or raw_event.get("invoice") or {}

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="b2b_history_analyst",
        message="Analyzing payment history and prior follow-ups",
        metadata={"parent": "overdue_receivable_specialist", "sub_node": True},
    )

    previous_followups = investigation.get("previous_followups") or signals.get("previous_followups") or 0
    response_behavior = investigation.get("response_behavior") or signals.get("response_behavior") or "none"
    customer_history = investigation.get("customer_history", {})

    # ── Source of truth: compute score from AR invoice ledger (not UI guess) ──
    score_result = await get_buyer_payment_score(
        company_name=invoice.get("company_name"),
        buyer_email=customer.get("email"),
        case_id=case_id,
        buyer_id=invoice.get("invoice_id"),
    )
    payment_history_score = score_result["payment_history_score"]

    # Optional form override — only for judge demos if they force a value AND
    # we want to show "what-if". Prefer computed score always for honesty.
    ui_override = signals.get("payment_history_score")
    score_source = "computed_from_invoice_ledger"
    if ui_override is not None and abs(float(ui_override) - payment_history_score) > 0.05:
        # Keep both visible; agent uses computed as primary
        score_source = "computed_from_invoice_ledger (UI override ignored for decisioning)"

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.15,
    )
    structured_llm = llm.with_structured_output(HistoryAnalystOutput)

    prompt = f"""You are a B2B History Analyst sub-agent within the Overdue Receivable Specialist.

Review buyer payment behavior and prior collections attempts.

COMPUTED PAYMENT HISTORY SCORE (from closed invoices — source of truth):
- Score: {payment_history_score}
- Formula: {score_result.get('formula')}
- Components: {score_result.get('components')}
- Ledger source: {score_result.get('ledger_source')}
- Data note: {score_result.get('data_source')}

Investigation so far:
{investigation}

Signals:
- Previous follow-ups: {previous_followups}
- Response behavior: {response_behavior}
- UI override field (informational only): {ui_override}
- Customer history tool: {customer_history}

Determine:
1. payer_reliability: EXCELLENT | GOOD | FAIR | POOR  (align with the computed score)
2. historical_on_time_rate (0-1) — prefer the computed on_time_rate component
3. previous_followups count
4. response_pattern summary (e.g. ignores reminders, promises then delays, disputes)
5. risk_flags list (e.g. chronic_late_payer, dispute_risk, high_value_exposure)
6. findings summary — mention that score came from invoice payment history

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
        # Judge-facing audit of score origin
        "payment_history_score": payment_history_score,
        "payment_score_source": score_source,
        "payment_score_breakdown": {
            "formula": score_result.get("formula"),
            "components": score_result.get("components"),
            "weights": score_result.get("weights"),
            "ledger_source": score_result.get("ledger_source"),
            "buyer_key": score_result.get("buyer_key"),
            "invoice_count": score_result.get("invoice_count"),
            "production_note": score_result.get("production_note"),
            "ui_override_ignored": ui_override,
        },
    }

    investigation["history_analysis"] = history_analysis
    investigation["payment_history_score"] = payment_history_score

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="b2b_history_analyst",
        message=(
            f"Reliability {result.payer_reliability} · "
            f"Score {payment_history_score:.0%} (from invoice ledger) · "
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
