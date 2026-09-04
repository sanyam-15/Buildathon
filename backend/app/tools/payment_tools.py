"""Tool functions used by agents — these call providers, never external APIs directly."""

from typing import Optional
from app.services.payment_provider import get_payment_provider
from app.services.communication_provider import get_communication_provider
from app.services.event_bus import event_bus


async def create_payment_link(
    amount: float,
    currency: str,
    customer_name: str,
    customer_email: str,
    customer_phone: Optional[str],
    reference_id: str,
    description: str,
    case_id: str,
) -> dict:
    """Create a payment link using the configured provider."""
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_started",
        agent="execution_agent",
        message=f"Creating payment link for ₹{amount:,.0f}",
        metadata={"tool": "create_payment_link", "amount": amount},
    )
    
    provider = get_payment_provider()
    result = await provider.create_payment_link(
        amount=amount,
        currency=currency,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        reference_id=reference_id,
        description=description,
    )
    
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="payment_link_created",
        agent="execution_agent",
        message=f"Payment link generated: {result['url']}",
        metadata={"tool": "create_payment_link", "result": result},
    )
    
    return result


async def send_email(
    recipient: str,
    subject: str,
    body: str,
    recovery_case_id: str,
    case_id: str,
) -> dict:
    """Send an email using the configured provider."""
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_started",
        agent="execution_agent",
        message=f"Sending recovery email to {recipient}",
        metadata={"tool": "send_email", "recipient": recipient},
    )
    
    provider = get_communication_provider()
    result = await provider.send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        recovery_case_id=recovery_case_id,
    )
    
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="communication_sent",
        agent="execution_agent",
        message=f"Email sent to {recipient} ({result.get('provider', 'unknown')} mode)",
        metadata={"tool": "send_email", "result": result},
    )
    
    return result


async def send_whatsapp(
    recipient: str,
    message: str,
    recovery_case_id: str,
    case_id: str,
) -> dict:
    """Send a WhatsApp message using the configured provider."""
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_started",
        agent="execution_agent",
        message=f"Sending WhatsApp message to {recipient}",
        metadata={"tool": "send_whatsapp", "recipient": recipient},
    )
    
    provider = get_communication_provider()
    result = await provider.send_whatsapp(
        recipient=recipient,
        message=message,
        recovery_case_id=recovery_case_id,
    )
    
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="communication_sent",
        agent="execution_agent",
        message=f"WhatsApp sent to {recipient} ({result.get('provider', 'unknown')} mode)",
        metadata={"tool": "send_whatsapp", "result": result},
    )
    
    return result


async def retry_payment(
    payment_id: str,
    case_id: str,
) -> dict:
    """Attempt to retry a failed payment (mock)."""
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_started",
        agent="execution_agent",
        message=f"Retrying payment {payment_id}",
        metadata={"tool": "retry_payment"},
    )
    
    # In mock mode, retry always "submits" but actual success comes via webhook
    result = {"status": "retry_submitted", "payment_id": payment_id}
    
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_completed",
        agent="execution_agent",
        message="Payment retry submitted",
        metadata={"tool": "retry_payment", "result": result},
    )
    
    return result


async def get_customer_history(
    customer_email: str,
    case_id: str,
) -> dict:
    """Get customer history (mock data for MVP)."""
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_started",
        agent="specialist",
        message=f"Looking up customer history for {customer_email}",
        metadata={"tool": "get_customer_history"},
    )
    
    # Mock customer history
    import random
    history = {
        "total_orders": random.randint(1, 20),
        "total_spent": round(random.uniform(1000, 50000), 2),
        "successful_payments": random.randint(3, 15),
        "failed_payments": random.randint(0, 3),
        "last_purchase_days_ago": random.randint(1, 90),
        "customer_since_months": random.randint(1, 36),
        "payment_success_rate": round(random.uniform(0.7, 0.98), 2),
    }
    
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_completed",
        agent="specialist",
        message=f"Customer has {history['total_orders']} orders, {history['payment_success_rate']*100:.0f}% payment success rate",
        metadata={"tool": "get_customer_history", "result": history},
    )
    
    return history


async def get_buyer_payment_score(
    company_name: Optional[str],
    buyer_email: Optional[str],
    case_id: str,
    buyer_id: Optional[str] = None,
) -> dict:
    """
    Compute B2B payment_history_score from historical invoices (demo ERP ledger).

    This is the judge-facing source of truth — score is derived by formula,
    not invented by the LLM or typed blindly into the form.
    """
    from app.services.payment_score import score_buyer

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_started",
        agent="b2b_history_analyst",
        message=(
            f"Computing payment history score from AR ledger "
            f"({company_name or buyer_email or 'buyer'})"
        ),
        metadata={
            "tool": "get_buyer_payment_score",
            "company_name": company_name,
            "buyer_email": buyer_email,
        },
    )

    result = score_buyer(
        company_name=company_name,
        buyer_email=buyer_email,
        buyer_id=buyer_id,
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="finding",
        agent="b2b_history_analyst",
        message=(
            f"Payment history score = {result['payment_history_score']:.0%} "
            f"from {result['invoice_count']} closed invoices "
            f"[{result['ledger_source']}] — {result['formula']}"
        ),
        metadata={"tool": "get_buyer_payment_score", "result": result},
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="tool_completed",
        agent="b2b_history_analyst",
        message=(
            f"Score computed: {result['payment_history_score']:.3f} "
            f"(source: historical invoices, not UI field)"
        ),
        metadata={"tool": "get_buyer_payment_score", "score": result["payment_history_score"]},
    )

    return result
