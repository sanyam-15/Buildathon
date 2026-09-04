"""B2B Invoice Analyzer sub-agent — ages and tiers overdue invoices."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import InvoiceAnalyzerOutput
from langchain_openai import ChatOpenAI
from app.config import settings


def _aging_bucket(days: int) -> str:
    if days <= 0:
        return "CURRENT"
    if days <= 30:
        return "1_30"
    if days <= 60:
        return "31_60"
    if days <= 90:
        return "61_90"
    return "90_PLUS"


async def b2b_invoice_analyzer(state: RecoveryState) -> dict:
    """Analyze invoice value, aging, and urgency for B2B collections."""
    case_id = state["case_id"]
    investigation = dict(state.get("investigation") or {})
    invoice = state.get("invoice") or investigation.get("invoice") or {}
    amount = state.get("amount_at_risk", 0)
    days_overdue = investigation.get("days_overdue") or invoice.get("days_overdue") or 0

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="b2b_invoice_analyzer",
        message="Analyzing invoice aging and value tier",
        metadata={"parent": "overdue_receivable_specialist", "sub_node": True},
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(InvoiceAnalyzerOutput)

    prompt = f"""You are a B2B Invoice Analyzer sub-agent within the Overdue Receivable Specialist.

Analyze this overdue invoice:

Invoice: {invoice}
Amount at risk: ₹{amount:,.0f}
Days overdue: {days_overdue}
Suggested aging bucket: {_aging_bucket(int(days_overdue))}
Prior investigation: {investigation}

Determine:
1. aging_bucket: CURRENT | 1_30 | 31_60 | 61_90 | 90_PLUS
2. invoice_tier: HIGH (>₹50k), MEDIUM (₹10k-50k), LOW (<₹10k) — adjust for context
3. urgency based on aging + value
4. findings summary
5. recommended_tone: soft | firm | formal | escalate

Be precise and collections-aware.
"""

    result: InvoiceAnalyzerOutput = await structured_llm.ainvoke(prompt)

    invoice_analysis = {
        "aging_bucket": result.aging_bucket,
        "invoice_tier": result.invoice_tier,
        "urgency": result.urgency,
        "findings": result.findings,
        "recommended_tone": result.recommended_tone,
        "days_overdue": days_overdue,
        "amount": amount,
    }

    investigation["invoice_analysis"] = invoice_analysis

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="b2b_invoice_analyzer",
        message=(
            f"Aging {result.aging_bucket} · Tier {result.invoice_tier} · "
            f"Urgency {result.urgency} · Tone: {result.recommended_tone}"
        ),
        metadata=invoice_analysis,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="b2b_invoice_analyzer",
        message=f"Invoice analysis complete: {result.findings}",
        metadata=invoice_analysis,
    )

    return {
        "investigation": investigation,
        "audit_trail": [{"agent": "b2b_invoice_analyzer", "action": "invoice_analysis", "result": invoice_analysis}],
    }
