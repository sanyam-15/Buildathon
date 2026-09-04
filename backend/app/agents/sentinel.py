"""Revenue Sentinel Agent — detects revenue risk in merchant events."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import SentinelOutput, PriorityLevel
from langchain_openai import ChatOpenAI
from app.config import settings


async def revenue_sentinel(state: RecoveryState) -> dict:
    """Analyze merchant event and detect revenue at risk."""
    case_id = state["case_id"]
    raw_event = state["raw_event"]

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="revenue_sentinel",
        message="Analyzing merchant event signals for revenue risk",
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(SentinelOutput)

    prompt = f"""You are a Revenue Sentinel AI agent. Your job is to analyze merchant event data and determine if there is revenue at risk.

Analyze the following merchant event and determine:
1. Is revenue at risk? (true/false)
2. How much revenue is at risk?
3. What is the priority level? (CRITICAL for amounts > 10000, HIGH for > 5000, MEDIUM for > 1000, LOW otherwise)
4. Why is this a revenue risk?
5. How urgent is the recovery? (0-1 score)
6. What is the estimated probability of successful recovery? (0-1 score)

Consider:
- Amount size and significance
- Customer information available
- Payment signals (failed, abandoned, etc.)
- Time sensitivity

Merchant Event Data:
{raw_event}
"""

    result: SentinelOutput = await structured_llm.ainvoke(prompt)

    risk_data = {
        "revenue_at_risk": result.revenue_at_risk,
        "amount_at_risk": result.amount_at_risk,
        "priority": result.priority.value,
        "reason": result.reason,
        "urgency_score": result.urgency_score,
        "recovery_probability": result.recovery_probability,
    }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="revenue_sentinel",
        message=f"₹{result.amount_at_risk:,.0f} revenue at risk — Priority: {result.priority.value}",
        metadata=risk_data,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="revenue_sentinel",
        message=f"Revenue risk assessment complete: {result.reason}",
        metadata=risk_data,
    )

    return {
        "revenue_risk": risk_data,
        "amount_at_risk": result.amount_at_risk,
        "status": "PROCESSING",
        "audit_trail": [{"agent": "revenue_sentinel", "action": "risk_assessment", "result": risk_data}],
    }
