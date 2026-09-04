"""B2B Follow-up Planner sub-agent — decide remind / wait / escalate / stop."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.schemas.agent import FollowupPlannerOutput
from langchain_openai import ChatOpenAI
from app.config import settings

# Bounded autonomy for B2B collections
MAX_B2B_FOLLOWUPS = 5
COOLDOWN_AFTER_ACK_HOURS = 48
COOLDOWN_AFTER_PROMISE_HOURS = 72


async def b2b_followup_planner(state: RecoveryState) -> dict:
    """Decide the next collections follow-up action with stopping rules."""
    case_id = state["case_id"]
    investigation = dict(state.get("investigation") or {})
    amount = state.get("amount_at_risk", 0)
    replan_count = state.get("replan_count", 0)

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_started",
        agent="b2b_followup_planner",
        message="Planning next B2B follow-up action (remind / wait / escalate / stop)",
        metadata={"parent": "overdue_receivable_specialist", "sub_node": True},
    )

    invoice_analysis = investigation.get("invoice_analysis", {})
    history_analysis = investigation.get("history_analysis", {})
    previous_followups = history_analysis.get("previous_followups") or investigation.get("previous_followups") or 0
    response_behavior = (
        history_analysis.get("response_behavior")
        or investigation.get("response_behavior")
        or "none"
    )

    # Deterministic guardrails before LLM
    hard_stop = False
    hard_escalate = False
    hard_wait = False
    hard_reason = ""

    if previous_followups >= MAX_B2B_FOLLOWUPS:
        hard_stop = True
        hard_reason = f"Max follow-up attempts ({MAX_B2B_FOLLOWUPS}) reached"
    elif response_behavior == "disputed":
        hard_escalate = True
        hard_reason = "Invoice disputed — requires human collections"
    elif response_behavior == "promised_payment" and previous_followups > 0:
        hard_wait = True
        hard_reason = f"Buyer promised payment — cooldown {COOLDOWN_AFTER_PROMISE_HOURS}h"
    elif response_behavior == "acknowledged" and previous_followups > 0 and replan_count == 0:
        hard_wait = True
        hard_reason = f"Buyer acknowledged — soft cooldown {COOLDOWN_AFTER_ACK_HOURS}h"

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(FollowupPlannerOutput)

    prompt = f"""You are a B2B Follow-up Planner sub-agent within the Overdue Receivable Specialist.

Your job: decide whether to REMIND, WAIT, ESCALATE, STOP, or CREATE_PAYMENT_LINK.

Context:
- Amount: ₹{amount:,.0f}
- Replan count: {replan_count}
- Previous follow-ups: {previous_followups}
- Response behavior: {response_behavior}
- Invoice analysis: {invoice_analysis}
- History analysis: {history_analysis}
- Full investigation: {investigation}

Hard constraints already evaluated:
- hard_stop={hard_stop}, hard_escalate={hard_escalate}, hard_wait={hard_wait}
- hard_reason={hard_reason or 'none'}

Rules:
- REMIND: send a personalized invoice reminder / payment link when contact is warranted
- WAIT: schedule delayed follow-up (set cooldown_hours) when buyer acknowledged/promised or timing is bad
- ESCALATE: human collections for disputes, high-value stuck accounts, or repeated ignores after many attempts
- STOP: further contact not worthwhile (max attempts, chronic non-responder with low recovery confidence)
- CREATE_PAYMENT_LINK: reduce friction for willing payers

If a hard constraint applies, respect it.
Provide clear reasoning and confidence.
"""

    result: FollowupPlannerOutput = await structured_llm.ainvoke(prompt)

    recommended = result.recommended_action.upper()
    if hard_stop:
        recommended = "STOP"
    elif hard_escalate:
        recommended = "ESCALATE"
    elif hard_wait and recommended not in ("STOP", "ESCALATE"):
        recommended = "WAIT"

    followup_plan = {
        "recommended_action": recommended,
        "cooldown_hours": (
            COOLDOWN_AFTER_PROMISE_HOURS
            if response_behavior == "promised_payment"
            else (COOLDOWN_AFTER_ACK_HOURS if response_behavior == "acknowledged" else result.cooldown_hours)
        ),
        "escalation_reason": hard_reason if hard_escalate else result.escalation_reason,
        "stop_reason": hard_reason if hard_stop else result.stop_reason,
        "confidence": result.confidence,
        "reasoning": hard_reason or result.reasoning,
        "max_followups": MAX_B2B_FOLLOWUPS,
        "previous_followups": previous_followups,
    }

    investigation["followup_plan"] = followup_plan
    investigation["recommended_approach"] = recommended

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="followup_planned",
        agent="b2b_followup_planner",
        message=(
            f"Follow-up plan: {recommended}"
            + (f" (wait {followup_plan['cooldown_hours']}h)" if recommended == "WAIT" else "")
            + f" — {followup_plan['reasoning']}"
        ),
        metadata=followup_plan,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="b2b_followup_planner",
        message=f"B2B follow-up plan ready: {recommended}",
        metadata=followup_plan,
    )

    return {
        "investigation": investigation,
        "audit_trail": [{"agent": "b2b_followup_planner", "action": "followup_plan", "result": followup_plan}],
    }
