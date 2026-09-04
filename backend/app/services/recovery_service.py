"""Recovery service — orchestrates LangGraph execution and database operations."""

import uuid
import asyncio
import random
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from app.graph.workflow import recovery_graph
from app.graph.state import RecoveryState
from app.services.event_bus import event_bus
from app.database.database import async_session
from app.models.recovery_case import RecoveryCase
from app.models.event import RevenueEvent
from app.models.customer import Customer
from app.schemas.events import RecoveryEventInput, BatchRecoveryInput
from sqlalchemy import select, func as sql_func


async def start_recovery(event_input: RecoveryEventInput) -> dict:
    """Start a new recovery workflow — creates case, runs LangGraph graph."""
    case_id = f"case_{uuid.uuid4().hex[:8]}"
    event_id = f"evt_{uuid.uuid4().hex[:8]}"

    # Build raw event (what the AI sees)
    raw_event = {
        "event_id": event_id,
        "customer": event_input.customer.model_dump(),
        "amount": event_input.amount,
        "currency": event_input.currency,
        "product_name": event_input.product_name,
        "merchant_name": event_input.merchant_name,
        "signals": event_input.signals.model_dump(),
    }
    if event_input.cart_items:
        raw_event["cart_items"] = [item.model_dump() for item in event_input.cart_items]
    if event_input.subscription_id:
        raw_event["subscription_id"] = event_input.subscription_id

    # Persist event and case to DB
    async with async_session() as session:
        # Upsert customer
        result = await session.execute(
            select(Customer).where(Customer.email == event_input.customer.email)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            customer = Customer(
                name=event_input.customer.name,
                email=event_input.customer.email,
                phone=event_input.customer.phone,
            )
            session.add(customer)
            await session.flush()

        revenue_event = RevenueEvent(
            id=event_id,
            raw_payload=raw_event,
            amount_at_risk=event_input.amount,
        )
        session.add(revenue_event)

        recovery_case = RecoveryCase(
            id=case_id,
            event_id=event_id,
            customer_id=customer.id,
            amount_at_risk=event_input.amount,
            status="CREATED",
        )
        session.add(recovery_case)
        await session.commit()

    # Emit case created event
    await event_bus.emit_simple(
        case_id=case_id,
        event_type="case_created",
        message=f"Recovery case created for ₹{event_input.amount:,.0f}",
        metadata={"event_id": event_id, "amount": event_input.amount},
    )

    # Build initial state
    initial_state: RecoveryState = {
        "case_id": case_id,
        "event_id": event_id,
        "raw_event": raw_event,
        "customer": event_input.customer.model_dump(),
        "transaction": {"amount": event_input.amount, "currency": event_input.currency},
        "cart": {"items": [i.model_dump() for i in event_input.cart_items]} if event_input.cart_items else None,
        "subscription": {"id": event_input.subscription_id} if event_input.subscription_id else None,
        "revenue_risk": None,
        "leakage_category": None,
        "classification_confidence": None,
        "classification_reason": None,
        "investigation": None,
        "strategy": None,
        "policy_result": None,
        "execution_results": [],
        "payment_link": None,
        "communication_results": [],
        "monitor_status": None,
        "retry_count": 0,
        "replan_count": 0,
        "status": "CREATED",
        "amount_at_risk": event_input.amount,
        "recovered_amount": 0.0,
        "audit_trail": [],
        "error": None,
    }

    # Run LangGraph in background task
    asyncio.create_task(_run_graph(case_id, initial_state))

    return {"case_id": case_id, "event_id": event_id, "status": "PROCESSING"}


async def _run_graph(case_id: str, initial_state: RecoveryState):
    """Run the LangGraph workflow and update database with final state."""
    try:
        final_state = await recovery_graph.ainvoke(initial_state)

        # Update recovery case in DB
        async with async_session() as session:
            result = await session.execute(
                select(RecoveryCase).where(RecoveryCase.id == case_id)
            )
            case = result.scalar_one_or_none()
            if case:
                case.category = final_state.get("leakage_category")
                case.classification_confidence = final_state.get("classification_confidence")
                case.amount_at_risk = final_state.get("amount_at_risk", 0)
                case.recovery_probability = final_state.get("strategy", {}).get("expected_recovery_probability") if final_state.get("strategy") else None
                case.status = final_state.get("status", "FAILED")
                case.selected_strategy = final_state.get("strategy")
                case.strategy_reasoning = {
                    "alternatives": final_state.get("strategy", {}).get("alternatives_considered", [])
                } if final_state.get("strategy") else None
                case.recovered_amount = final_state.get("recovered_amount", 0)
                case.retry_count = final_state.get("retry_count", 0)
                case.replan_count = final_state.get("replan_count", 0)
                case.investigation = final_state.get("investigation")
                case.policy_result = final_state.get("policy_result")
                case.execution_results = final_state.get("execution_results")
                await session.commit()

    except Exception as e:
        import traceback
        traceback.print_exc()
        await event_bus.emit_simple(
            case_id=case_id,
            event_type="case_failed",
            message=f"Recovery workflow failed: {str(e)}",
            metadata={"error": str(e)},
        )
        # Update case status to FAILED
        async with async_session() as session:
            result = await session.execute(
                select(RecoveryCase).where(RecoveryCase.id == case_id)
            )
            case = result.scalar_one_or_none()
            if case:
                case.status = "FAILED"
                await session.commit()



async def get_case(case_id: str) -> Optional[dict]:
    """Get a recovery case by ID."""
    async with async_session() as session:
        result = await session.execute(
            select(RecoveryCase).where(RecoveryCase.id == case_id)
        )
        case = result.scalar_one_or_none()
        if not case:
            return None
        return {
            "id": case.id,
            "event_id": case.event_id,
            "customer_id": case.customer_id,
            "category": case.category,
            "classification_confidence": case.classification_confidence,
            "amount_at_risk": case.amount_at_risk,
            "recovery_probability": case.recovery_probability,
            "status": case.status,
            "selected_strategy": case.selected_strategy,
            "strategy_reasoning": case.strategy_reasoning,
            "recovered_amount": case.recovered_amount,
            "retry_count": case.retry_count,
            "replan_count": case.replan_count,
            "investigation": case.investigation,
            "policy_result": case.policy_result,
            "execution_results": case.execution_results,
            "created_at": str(case.created_at) if case.created_at else None,
            "updated_at": str(case.updated_at) if case.updated_at else None,
        }


async def get_all_cases() -> List[dict]:
    """Get all recovery cases."""
    async with async_session() as session:
        result = await session.execute(
            select(RecoveryCase).order_by(RecoveryCase.created_at.desc())
        )
        cases = result.scalars().all()
        return [
            {
                "id": c.id,
                "event_id": c.event_id,
                "category": c.category,
                "amount_at_risk": c.amount_at_risk,
                "recovery_probability": c.recovery_probability,
                "status": c.status,
                "recovered_amount": c.recovered_amount,
                "created_at": str(c.created_at) if c.created_at else None,
            }
            for c in cases
        ]


async def get_dashboard_stats() -> dict:
    """Get aggregate dashboard statistics."""
    async with async_session() as session:
        total = await session.execute(select(sql_func.count(RecoveryCase.id)))
        total_count = total.scalar() or 0

        at_risk = await session.execute(select(sql_func.sum(RecoveryCase.amount_at_risk)))
        total_at_risk = at_risk.scalar() or 0

        recovered = await session.execute(select(sql_func.sum(RecoveryCase.recovered_amount)))
        total_recovered = recovered.scalar() or 0

        active = await session.execute(
            select(sql_func.count(RecoveryCase.id)).where(
                RecoveryCase.status.in_(["CREATED", "PROCESSING", "WAITING_FOR_PAYMENT"])
            )
        )
        active_count = active.scalar() or 0

        recovered_count = await session.execute(
            select(sql_func.count(RecoveryCase.id)).where(RecoveryCase.status == "RECOVERED")
        )
        recovered_cases = recovered_count.scalar() or 0

        failed_count = await session.execute(
            select(sql_func.count(RecoveryCase.id)).where(RecoveryCase.status == "FAILED")
        )
        failed_cases = failed_count.scalar() or 0

        escalated_count = await session.execute(
            select(sql_func.count(RecoveryCase.id)).where(RecoveryCase.status == "ESCALATED")
        )
        escalated_cases = escalated_count.scalar() or 0

        from app.models.payment import PaymentLink
        from app.models.audit_log import Communication
        
        pl_count = await session.execute(select(sql_func.count(PaymentLink.id)))
        payment_links = pl_count.scalar() or 0

        email_count = await session.execute(
            select(sql_func.count(Communication.id)).where(Communication.channel == "email")
        )
        emails = email_count.scalar() or 0

    recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0

    return {
        "total_cases": total_count,
        "total_at_risk": total_at_risk,
        "total_recovered": total_recovered,
        "recovery_rate": round(recovery_rate, 1),
        "active_cases": active_count,
        "recovered_cases": recovered_cases,
        "failed_cases": failed_cases,
        "escalated_cases": escalated_cases,
        "payment_links_generated": payment_links,
        "emails_sent": emails,
        "retries_attempted": 0,
    }


async def start_batch_recovery(batch_input: BatchRecoveryInput) -> dict:
    """Start batch recovery for multiple events."""
    events = batch_input.events or _generate_batch_events(
        count=batch_input.count or 10,
        customer_email=batch_input.customer_email,
        customer_phone=batch_input.customer_phone,
    )

    case_ids = []
    for event_input in events:
        result = await start_recovery(event_input)
        case_ids.append(result["case_id"])
        await asyncio.sleep(0.5)  # Stagger to avoid rate limits

    return {
        "total_events": len(events),
        "case_ids": case_ids,
        "status": "BATCH_PROCESSING",
    }


def _generate_batch_events(
    count: int = 10,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
) -> List[RecoveryEventInput]:
    """Generate a batch of diverse recovery events."""
    from app.schemas.events import RecoveryEventInput, CustomerInput, SignalsInput, CartItem

    names = ["Aarav Patel", "Priya Sharma", "Rohan Gupta", "Ananya Reddy", "Vikram Singh",
             "Meera Joshi", "Arjun Nair", "Divya Iyer", "Karan Malhotra", "Sneha Das",
             "Rahul Verma", "Pooja Mehta"]
    products = ["Premium Plan", "Annual Subscription", "Pro Features", "Enterprise License",
                "Starter Pack", "Growth Bundle", "Designer Toolkit", "Analytics Suite"]

    events = []
    for i in range(count):
        name = random.choice(names)
        email = customer_email or f"{name.lower().replace(' ', '.')}@example.com"
        phone = customer_phone or f"+9199{random.randint(10000000, 99999999)}"
        amount = random.choice([499, 999, 1999, 2499, 4999, 7499, 9999, 14999, 24999])
        product = random.choice(products)

        # Mix event types
        event_type = random.choices(
            ["failed_payment", "abandoned_cart", "subscription_failure"],
            weights=[0.4, 0.4, 0.2],
        )[0]

        if event_type == "failed_payment":
            signals = SignalsInput(
                payment_attempted=True,
                payment_status="failed",
                failure_reason=random.choice(["insufficient_funds", "card_declined", "bank_timeout", "expired_card"]),
            )
        elif event_type == "abandoned_cart":
            signals = SignalsInput(
                cart_created=True,
                checkout_started=random.choice([True, False]),
                payment_attempted=False,
                inactive_minutes=random.choice([30, 60, 120, 240, 480]),
            )
        else:  # subscription_failure
            signals = SignalsInput(
                renewal_attempted=True,
                renewal_status="failed",
                failure_reason=random.choice(["card_expired", "insufficient_funds"]),
            )

        events.append(RecoveryEventInput(
            customer=CustomerInput(name=name, email=email, phone=phone),
            amount=amount,
            product_name=product,
            signals=signals,
            cart_items=[CartItem(name=product, quantity=1, price=amount)] if event_type == "abandoned_cart" else None,
        ))

    return events
