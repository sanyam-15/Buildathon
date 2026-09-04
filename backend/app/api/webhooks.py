"""Webhook endpoints for payment providers."""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from app.services.event_bus import event_bus
from app.database.database import async_session
from app.models.payment import PaymentLink
from sqlalchemy import select
from datetime import datetime, timezone

router = APIRouter()


class MockWebhookPayload(BaseModel):
    payment_link_id: str
    status: str = "paid"


@router.post("/payment")
async def handle_mock_webhook(payload: MockWebhookPayload):
    """Handle webhook from the mock checkout page."""
    
    async with async_session() as session:
        result = await session.execute(
            select(PaymentLink).where(PaymentLink.id == payload.payment_link_id)
        )
        link = result.scalar_one_or_none()
        
        if not link:
            raise HTTPException(status_code=404, detail="Payment link not found")
        
        case_id = link.recovery_case_id
        
        if payload.status == "paid":
            link.status = "paid"
            link.paid_at = datetime.now(timezone.utc)
            await session.commit()
            
            # Emit webhook received event
            await event_bus.emit_simple(
                case_id=case_id,
                event_type="webhook_received",
                agent="system",
                message="Payment webhook received from Mock Provider",
                metadata={"payment_link_id": payload.payment_link_id, "status": "paid"}
            )
            
            # Notify Monitor Agent that payment was successful
            # In a real system, the Monitor Agent might be sleeping or we might wake it up.
            # Here, we update the state directly via the event bus which the frontend will see,
            # and we also need to update the RecoveryCase status in DB.
            from app.models.recovery_case import RecoveryCase
            case_result = await session.execute(select(RecoveryCase).where(RecoveryCase.id == case_id))
            case = case_result.scalar_one_or_none()
            if case:
                case.status = "RECOVERED"
                case.recovered_amount = link.amount
                await session.commit()
            
            # Emit the final events that the Monitor Agent would normally emit
            await event_bus.emit_simple(
                case_id=case_id,
                event_type="payment_verified",
                agent="monitor_agent",
                message=f"Payment verified via webhook — ₹{link.amount:,.0f} recovered",
                metadata={"amount": link.amount}
            )
            
            await event_bus.emit_simple(
                case_id=case_id,
                event_type="revenue_recovered",
                agent="monitor_agent",
                message=f"💰 Revenue recovered: ₹{link.amount:,.0f}",
                metadata={"amount": link.amount}
            )
            
            await event_bus.emit_simple(
                case_id=case_id,
                event_type="case_completed",
                agent="system",
                message="Recovery case completed successfully",
            )
            
    return {"status": "success"}


@router.get("/razorpay")
async def handle_razorpay_callback(request: Request):
    """Handle Razorpay payment callback (GET redirect after payment).
    
    Razorpay redirects the customer here after payment with query params:
    - razorpay_payment_id
    - razorpay_payment_link_id
    - razorpay_payment_link_reference_id  (our case_id)
    - razorpay_payment_link_status
    - razorpay_signature
    """
    import hmac
    import hashlib
    from fastapi.responses import RedirectResponse
    from app.config import settings
    from app.models.recovery_case import RecoveryCase

    params = request.query_params
    payment_id = params.get("razorpay_payment_id", "")
    payment_link_id = params.get("razorpay_payment_link_id", "")
    reference_id = params.get("razorpay_payment_link_reference_id", "")
    link_status = params.get("razorpay_payment_link_status", "")
    signature = params.get("razorpay_signature", "")

    # Build the redirect URL early so we can redirect even on error
    frontend_url = settings.FRONTEND_URL

    if not reference_id or link_status != "paid":
        return RedirectResponse(url=frontend_url, status_code=303)

    # Verify Razorpay signature (HMAC SHA256)
    # The payload for callback signature is:
    #   payment_link_id + '|' + reference_id + '|' + payment_link_status + '|' + razorpay_payment_id
    if settings.RAZORPAY_KEY_SECRET and signature:
        payload_str = f"{payment_link_id}|{reference_id}|{link_status}|{payment_id}"
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            # Signature mismatch — log and still redirect, but don't process
            print(f"[WEBHOOK] Razorpay signature mismatch for case {reference_id}")
            return RedirectResponse(url=frontend_url, status_code=303)

    # Process payment
    case_id = reference_id

    async with async_session() as session:
        # Find the payment link by provider_link_id (Razorpay's plink_xxx)
        result = await session.execute(
            select(PaymentLink).where(PaymentLink.provider_link_id == payment_link_id)
        )
        link = result.scalar_one_or_none()

        # Fallback: find by recovery_case_id
        if not link:
            result = await session.execute(
                select(PaymentLink).where(PaymentLink.recovery_case_id == case_id)
            )
            link = result.scalar_one_or_none()

        if not link:
            print(f"[WEBHOOK] No payment link found for case {case_id} / plink {payment_link_id}")
            return RedirectResponse(url=frontend_url, status_code=303)

        # Update payment link
        link.status = "paid"
        link.paid_at = datetime.now(timezone.utc)
        amount = link.amount

        # Update recovery case
        case_result = await session.execute(
            select(RecoveryCase).where(RecoveryCase.id == case_id)
        )
        case = case_result.scalar_one_or_none()
        if case:
            case.status = "RECOVERED"
            case.recovered_amount = amount

        await session.commit()

    # Emit events so the frontend SSE stream picks them up
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="webhook_received",
        agent="system",
        message=f"Payment webhook received from Razorpay (payment: {payment_id})",
        metadata={
            "payment_link_id": payment_link_id,
            "razorpay_payment_id": payment_id,
            "status": "paid",
        },
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="payment_verified",
        agent="monitor_agent",
        message=f"Payment verified via Razorpay — ₹{amount:,.0f} recovered",
        metadata={"amount": amount, "razorpay_payment_id": payment_id},
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="revenue_recovered",
        agent="monitor_agent",
        message=f"💰 Revenue recovered: ₹{amount:,.0f}",
        metadata={"amount": amount},
    )

    await event_bus.emit_simple(
        case_id=case_id,
        event_type="case_completed",
        agent="system",
        message="Recovery case completed successfully",
    )

    # Redirect user to frontend dashboard
    return RedirectResponse(url=frontend_url, status_code=303)
