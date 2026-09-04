"""Leakage Classifier Agent — determines the type of revenue leakage."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import ClassifierOutput, LeakageCategory
from langchain_openai import ChatOpenAI
from app.config import settings


async def leakage_classifier(state: RecoveryState) -> dict:
    """Classify the type of revenue leakage from event signals."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]
    revenue_risk = state.get("revenue_risk", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="leakage_classifier",
        message="Analyzing event signals to determine leakage category",
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(ClassifierOutput)

    prompt = f"""You are a Leakage Classification AI agent. Your job is to analyze merchant event signals and classify the type of revenue leakage.

Categories:
1. FAILED_PAYMENT — Payment was attempted but failed (gateway error, insufficient funds, card declined, etc.) [B2C]
2. ABANDONED_CART — Customer added items to cart, possibly started checkout, but never completed payment [B2C]
3. SUBSCRIPTION_FAILURE — Subscription renewal was attempted but failed [B2C]
4. OVERDUE_RECEIVABLE — B2B invoice / receivable is past due; unpaid business invoice beyond due date [B2B]
5. UNKNOWN — Cannot determine category from available signals

Classification rules (use these signals):
- If invoice_overdue=true OR days_overdue > 0 with invoice context OR segment=B2B with overdue invoice → OVERDUE_RECEIVABLE
- If payment_attempted=true AND payment_status=failed → FAILED_PAYMENT
- If cart_created=true AND (payment_attempted=false OR payment_attempted is not present) AND inactive_minutes > 0 → ABANDONED_CART
- If checkout_started=true AND payment_attempted=false → ABANDONED_CART
- If renewal_attempted=true AND renewal_status=failed → SUBSCRIPTION_FAILURE
- If none of the above signals match clearly → UNKNOWN

Be precise. Use the signals provided. State which signals you used for classification.
Your confidence should reflect how clearly the signals indicate the category.

Event Data:
{raw_event}

Revenue Risk Assessment:
{revenue_risk}
"""

    result: ClassifierOutput = await structured_llm.ainvoke(prompt)

    # Deterministic signal validation to boost/reduce confidence
    signals = raw_event.get("signals", {})
    validated_category = result.category.value
    validated_confidence = result.confidence

    # Hard overrides based on deterministic signal checks
    # B2B overdue receivable takes priority when invoice signals present
    if (
        signals.get("invoice_overdue") is True
        or (signals.get("days_overdue") is not None and int(signals.get("days_overdue") or 0) > 0)
        or raw_event.get("segment") == "B2B"
        or raw_event.get("invoice")
    ):
        if signals.get("invoice_overdue") is True or raw_event.get("invoice") or (
            signals.get("days_overdue") is not None and int(signals.get("days_overdue") or 0) > 0
        ):
            validated_category = "OVERDUE_RECEIVABLE"
            validated_confidence = 0.96
    elif signals.get("payment_attempted") is True and signals.get("payment_status") == "failed":
        if validated_category != "FAILED_PAYMENT":
            validated_category = "FAILED_PAYMENT"
            validated_confidence = 0.95
    elif signals.get("checkout_started") is True and signals.get("payment_attempted") is False:
        if validated_category != "ABANDONED_CART":
            validated_category = "ABANDONED_CART"
            validated_confidence = 0.94
    elif signals.get("renewal_attempted") is True and signals.get("renewal_status") == "failed":
        if validated_category != "SUBSCRIPTION_FAILURE":
            validated_category = "SUBSCRIPTION_FAILURE"
            validated_confidence = 0.93

    classification_data = {
        "category": validated_category,
        "confidence": validated_confidence,
        "reason": result.reason,
        "signals_used": result.signals_used,
    }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="classification_complete",
        agent="leakage_classifier",
        message=f"Classified as {validated_category} ({validated_confidence*100:.0f}% confidence)",
        metadata=classification_data,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="leakage_classifier",
        message=f"Leakage classification complete: {result.reason}",
        metadata=classification_data,
    )

    # If confidence too low, escalate
    if validated_confidence < 0.5:
        return {
            "leakage_category": "UNKNOWN",
            "classification_confidence": validated_confidence,
            "classification_reason": result.reason,
            "status": "ESCALATED",
            "audit_trail": [{"agent": "leakage_classifier", "action": "classification", "result": classification_data, "note": "Low confidence — escalating"}],
        }

    segment = "B2B" if validated_category == "OVERDUE_RECEIVABLE" else (raw_event.get("segment") or "B2C")

    return {
        "leakage_category": validated_category,
        "classification_confidence": validated_confidence,
        "classification_reason": result.reason,
        "segment": segment,
        "audit_trail": [{"agent": "leakage_classifier", "action": "classification", "result": classification_data}],
    }
