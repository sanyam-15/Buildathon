"""Execution Agent — converts approved strategies into real actions via tools."""

from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.tools.payment_tools import create_payment_link, send_email, send_whatsapp, retry_payment


async def execution_agent(state: RecoveryState) -> dict:
    """Execute the approved recovery strategy using tools."""
    case_id = state["case_id"]
    strategy = state.get("strategy", {})
    customer = state.get("customer", {})
    amount = state.get("amount_at_risk", 0)
    raw_event = state.get("raw_event", {})

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="execution_started",
        agent="execution_agent",
        message="Starting recovery execution",
    )

    primary_action = strategy.get("primary_action", "STOP")
    comm_channel = strategy.get("communication_channel", "NONE")
    customer_name = customer.get("name", "Customer") if customer else "Customer"
    customer_email = customer.get("email", "") if customer else ""
    customer_phone = customer.get("phone", "") if customer else ""
    product_name = raw_event.get("product_name", "Product")

    execution_results = []
    payment_link_data = None
    communication_results = []

    # ── Action: SMART_RETRY ──
    if primary_action == "SMART_RETRY":
        result = await retry_payment(payment_id=f"retry_{case_id}", case_id=case_id)
        execution_results.append({"action": "SMART_RETRY", "result": result})

    # ── Action: CREATE_PAYMENT_LINK ──
    if primary_action in ("CREATE_PAYMENT_LINK", "SEND_EMAIL", "SEND_WHATSAPP"):
        # Always create payment link if communicating
        link_result = await create_payment_link(
            amount=amount,
            currency=raw_event.get("currency", "INR"),
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            reference_id=case_id,
            description=f"Recovery payment for {product_name}",
            case_id=case_id,
        )
        payment_link_data = link_result
        execution_results.append({"action": "CREATE_PAYMENT_LINK", "result": link_result})

    # ── Action: SEND_EMAIL ──
    if comm_channel == "EMAIL" or primary_action == "SEND_EMAIL":
        # Build email with real data (not LLM-invented)
        payment_url = payment_link_data.get("url", "#") if payment_link_data else "#"

        email_subject = strategy.get("email_subject") or f"Complete your purchase — ₹{amount:,.0f}"
        email_body_template = strategy.get("email_body") or (
            f"Hi {customer_name},\n\n"
            f"We noticed your purchase of ₹{amount:,.0f} for {product_name} was not completed.\n\n"
            f"You can securely complete your purchase using the link below:\n\n"
            f"{{payment_link}}\n\n"
            f"This link is secure and expires in 24 hours.\n\n"
            f"Thank you,\nRecoverAI"
        )

        # Replace placeholder with real payment link (LLM never invents URLs)
        email_body = email_body_template.replace("{payment_link}", payment_url)
        email_body = email_body.replace("{{payment_link}}", payment_url)

        email_result = await send_email(
            recipient=customer_email,
            subject=email_subject,
            body=email_body,
            recovery_case_id=case_id,
            case_id=case_id,
        )
        communication_results.append(email_result)
        execution_results.append({"action": "SEND_EMAIL", "result": email_result})

    # ── Action: SEND_WHATSAPP ──
    if comm_channel == "WHATSAPP" or primary_action == "SEND_WHATSAPP":
        payment_url = payment_link_data.get("url", "#") if payment_link_data else "#"
        wa_message = strategy.get("message_body") or (
            f"Hi {customer_name}, your purchase of ₹{amount:,.0f} is pending. "
            f"Complete it here: {payment_url}"
        )
        wa_message = wa_message.replace("{payment_link}", payment_url)
        wa_message = wa_message.replace("{{payment_link}}", payment_url)

        if customer_phone:
            wa_result = await send_whatsapp(
                recipient=customer_phone,
                message=wa_message,
                recovery_case_id=case_id,
                case_id=case_id,
            )
            communication_results.append(wa_result)
            execution_results.append({"action": "SEND_WHATSAPP", "result": wa_result})

    # ── Action: ESCALATE ──
    if primary_action == "ESCALATE_TO_HUMAN":
        await event_bus.emit_simple(
            case_id=case_id,
            event_type="case_escalated",
            agent="execution_agent",
            message="Case escalated to human agent for manual review",
        )
        return {
            "execution_results": [{"action": "ESCALATE_TO_HUMAN", "result": {"status": "escalated"}}],
            "status": "ESCALATED",
            "audit_trail": [{"agent": "execution_agent", "action": "escalation", "result": {"status": "escalated"}}],
        }

    # ── Action: STOP ──
    if primary_action == "STOP":
        await event_bus.emit_simple(
            case_id=case_id,
            event_type="case_completed",
            agent="execution_agent",
            message="Recovery stopped — no further action will be taken",
        )
        return {
            "execution_results": [{"action": "STOP", "result": {"status": "stopped"}}],
            "status": "FAILED",
            "audit_trail": [{"agent": "execution_agent", "action": "stop", "result": {"status": "stopped"}}],
        }

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="agent_completed",
        agent="execution_agent",
        message=f"Execution complete — {len(execution_results)} actions taken",
        metadata={"actions": [r["action"] for r in execution_results]},
    )

    return {
        "execution_results": execution_results,
        "payment_link": payment_link_data,
        "communication_results": communication_results,
        "monitor_status": "WAITING_FOR_PAYMENT",
        "audit_trail": [{"agent": "execution_agent", "action": "execution", "results": execution_results}],
    }
