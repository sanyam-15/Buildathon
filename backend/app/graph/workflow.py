"""LangGraph StateGraph workflow definition — the core orchestration engine.

This defines the multi-agent workflow as a directed graph with conditional edges.
Each node is an agent function that reads from and writes to the RecoveryState.
"""

from langgraph.graph import StateGraph, END
from app.graph.state import RecoveryState
from app.graph.routing import route_to_specialist, route_after_policy, route_after_monitor

# Import all agent nodes
from app.agents.sentinel import revenue_sentinel
from app.agents.classifier import leakage_classifier
from app.agents.failed_payment import failed_payment_specialist
from app.agents.abandoned_cart import abandoned_cart_specialist
from app.agents.subscription import subscription_specialist
from app.agents.strategist import recovery_strategist
from app.policies.recovery_policy import policy_engine
from app.agents.execution import execution_agent
from app.agents.monitor import monitor_agent
from app.services.event_bus import event_bus


async def replan_node(state: RecoveryState) -> dict:
    """Replan by incrementing replan count and routing back to strategist."""
    case_id = state["case_id"]
    replan_count = state.get("replan_count", 0) + 1

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="replan_started",
        agent="replan",
        message=f"Replanning recovery strategy (attempt {replan_count})",
        metadata={"replan_count": replan_count},
    )

    return {
        "replan_count": replan_count,
        "audit_trail": [{"agent": "replan", "action": "replan", "attempt": replan_count}],
    }


async def escalate_node(state: RecoveryState) -> dict:
    """Escalate case to human review."""
    case_id = state["case_id"]

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="case_escalated",
        agent="escalate",
        message="Case escalated to human agent — autonomous recovery limits reached",
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="case_completed",
        agent="escalate",
        message="Case completed with escalation status",
    )

    return {
        "status": "ESCALATED",
        "audit_trail": [{"agent": "escalate", "action": "escalation", "reason": "Autonomous limits reached"}],
    }


def build_recovery_graph() -> StateGraph:
    """Build and compile the recovery workflow graph."""

    graph = StateGraph(RecoveryState)

    # ── Add nodes ──
    graph.add_node("revenue_sentinel", revenue_sentinel)
    graph.add_node("leakage_classifier", leakage_classifier)
    graph.add_node("failed_payment_specialist", failed_payment_specialist)
    graph.add_node("abandoned_cart_specialist", abandoned_cart_specialist)
    graph.add_node("subscription_specialist", subscription_specialist)
    graph.add_node("recovery_strategist", recovery_strategist)
    graph.add_node("policy_engine", policy_engine)
    graph.add_node("execution_agent", execution_agent)
    graph.add_node("monitor_agent", monitor_agent)
    graph.add_node("replan", replan_node)
    graph.add_node("escalate", escalate_node)

    # ── Set entry point ──
    graph.set_entry_point("revenue_sentinel")

    # ── Linear edges ──
    graph.add_edge("revenue_sentinel", "leakage_classifier")

    # ── Conditional: Classifier → Specialist ──
    graph.add_conditional_edges(
        "leakage_classifier",
        route_to_specialist,
        {
            "failed_payment_specialist": "failed_payment_specialist",
            "abandoned_cart_specialist": "abandoned_cart_specialist",
            "subscription_specialist": "subscription_specialist",
            "escalate": "escalate",
        },
    )

    # ── Specialists → Strategy ──
    graph.add_edge("failed_payment_specialist", "recovery_strategist")
    graph.add_edge("abandoned_cart_specialist", "recovery_strategist")
    graph.add_edge("subscription_specialist", "recovery_strategist")

    # ── Strategy → Policy ──
    graph.add_edge("recovery_strategist", "policy_engine")

    # ── Conditional: Policy → Execution or Replan ──
    graph.add_conditional_edges(
        "policy_engine",
        route_after_policy,
        {
            "execution_agent": "execution_agent",
            "replan": "replan",
            "escalate": "escalate",
        },
    )

    # ── Replan → Strategy (loop back) ──
    graph.add_edge("replan", "recovery_strategist")

    # ── Execution → Monitor ──
    graph.add_edge("execution_agent", "monitor_agent")

    # ── Conditional: Monitor → End or Replan ──
    graph.add_conditional_edges(
        "monitor_agent",
        route_after_monitor,
        {
            "end": END,
            "replan": "replan",
            "escalate": "escalate",
        },
    )

    # ── Escalate → End ──
    graph.add_edge("escalate", END)

    return graph.compile()


# Compile the graph once at module load
recovery_graph = build_recovery_graph()
