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
    invoice = state.get("invoice") or raw_event.get("invoice") or {}
    invoice_id = invoice.get("invoice_id", "")
    company_name = invoice.get("company_name") or customer_name
    is_b2b = (
        state.get("segment") == "B2B"
        or state.get("leakage_category") == "OVERDUE_RECEIVABLE"
        or bool(invoice)
    )

    execution_results = []
    payment_link_data = None
    communication_results = []

    # ── Action: SMART_RETRY ──
    if primary_action == "SMART_RETRY":
        result = await retry_payment(payment_id=f"retry_{case_id}", case_id=case_id)
        execution_results.append({"action": "SMART_RETRY", "result": result})

    # ── Action: WAIT / SCHEDULE_FOLLOWUP ──
    if primary_action in ("WAIT", "SCHEDULE_FOLLOWUP"):
        followup_plan = (state.get("investigation") or {}).get("followup_plan", {})
        cooldown = followup_plan.get("cooldown_hours") or strategy.get("cooldown_hours") or 48
        wait_result = {
            "status": "scheduled",
            "cooldown_hours": cooldown,
            "reason": strategy.get("reason", "Deferred follow-up"),
        }
        await event_bus.emit_simple(
            case_id=case_id,
            event_type="followup_scheduled",
            agent="execution_agent",
            message=f"Follow-up scheduled — waiting {cooldown}h before next contact",
            metadata=wait_result,
        )
        execution_results.append({"action": primary_action, "result": wait_result})
        await event_bus.emit_simple(
            case_id=case_id,
            event_type="agent_completed",
            agent="execution_agent",
            message=f"Execution complete — deferred follow-up ({cooldown}h)",
            metadata={"actions": [primary_action]},
        )
        return {
            "execution_results": execution_results,
            "monitor_status": "WAITING_FOR_PAYMENT",
            "status": "WAITING_FOR_PAYMENT",
            "audit_trail": [{"agent": "execution_agent", "action": "schedule_followup", "result": wait_result}],
        }

    # ── Action: CREATE_PAYMENT_LINK / SEND_INVOICE_REMINDER / SEND_EMAIL / SEND_WHATSAPP ──
    if primary_action in (
        "CREATE_PAYMENT_LINK",
        "SEND_EMAIL",
        "SEND_WHATSAPP",
        "SEND_INVOICE_REMINDER",
        "OFFER_DISCOUNT",
    ):
        description = (
            f"Invoice payment for {invoice_id} — {company_name}"
            if is_b2b and invoice_id
            else f"Recovery payment for {product_name}"
        )
        link_result = await create_payment_link(
            amount=amount,
            currency=raw_event.get("currency", "INR"),
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            reference_id=case_id,
            description=description,
            case_id=case_id,
        )
        payment_link_data = link_result
        execution_results.append({"action": "CREATE_PAYMENT_LINK", "result": link_result})

    # ── Action: SEND_EMAIL / SEND_INVOICE_REMINDER ──
    if (
        comm_channel == "EMAIL"
        or primary_action in ("SEND_EMAIL", "SEND_INVOICE_REMINDER")
    ):
        payment_url = payment_link_data.get("url", "#") if payment_link_data else "#"

        if is_b2b:
            email_subject = strategy.get("email_subject") or (
                f"Payment reminder: Invoice {invoice_id} — ₹{amount:,.0f} overdue"
            )
            email_body_template = strategy.get("email_body") or (
                f"Dear {customer_name},\n\n"
                f"This is a reminder that invoice {invoice_id} for {company_name} "
                f"totaling ₹{amount:,.0f} remains unpaid.\n\n"
                f"You can settle the invoice securely using the link below:\n\n"
                f"{{payment_link}}\n\n"
                f"If payment has already been made, please disregard this message.\n\n"
                f"Regards,\nAccounts Receivable\nRazorpay Relay"
            )
        else:
            email_subject = strategy.get("email_subject") or f"Complete your purchase — ₹{amount:,.0f}"
            email_body_template = strategy.get("email_body") or (
                f"Hi {customer_name},\n\n"
                f"We noticed your purchase of ₹{amount:,.0f} for {product_name} was not completed.\n\n"
                f"You can securely complete your purchase using the link below:\n\n"
                f"{{payment_link}}\n\n"
                f"This link is secure and expires in 24 hours.\n\n"
                f"Thank you,\nRecoverAI"
            )

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
        action_label = "SEND_INVOICE_REMINDER" if primary_action == "SEND_INVOICE_REMINDER" else "SEND_EMAIL"
        execution_results.append({"action": action_label, "result": email_result})

    # ── Action: SEND_WHATSAPP ──
    if comm_channel == "WHATSAPP" or primary_action == "SEND_WHATSAPP":
        payment_url = payment_link_data.get("url", "#") if payment_link_data else "#"
        if is_b2b:
            wa_message = strategy.get("message_body") or (
                f"Hi {customer_name}, invoice {invoice_id} for ₹{amount:,.0f} is overdue. "
                f"Pay securely: {payment_url}"
            )
        else:
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
