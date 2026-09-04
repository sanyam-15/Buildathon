"""Payment provider abstraction with Mock and Razorpay implementations."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Protocol, Dict, Any

from app.config import settings
from app.database.database import async_session
from app.models.payment import PaymentLink


class PaymentProvider(Protocol):
    """Protocol for payment providers."""

    async def create_payment_link(
        self,
        amount: float,
        currency: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str],
        reference_id: str,
        description: str,
    ) -> Dict[str, Any]:
        """Create a payment link. Returns dict with url, provider_link_id, etc."""
        ...

    async def get_payment_status(self, payment_link_id: str) -> Dict[str, Any]:
        """Get payment status for a link."""
        ...


class MockPaymentProvider:
    """Mock payment provider for local development."""

    async def create_payment_link(
        self,
        amount: float,
        currency: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str],
        reference_id: str,
        description: str,
    ) -> Dict[str, Any]:
        link_id = f"mock_link_{uuid.uuid4().hex[:12]}"
        url = f"{settings.FRONTEND_URL}/pay/{link_id}"

        # Persist to DB
        async with async_session() as session:
            payment_link = PaymentLink(
                id=link_id,
                recovery_case_id=reference_id,
                provider="mock",
                provider_link_id=link_id,
                url=url,
                amount=amount,
                currency=currency,
                description=description,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                status="created",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            )
            session.add(payment_link)
            await session.commit()

        return {
            "provider": "mock",
            "link_id": link_id,
            "url": url,
            "amount": amount,
            "currency": currency,
            "status": "created",
        }

    async def get_payment_status(self, payment_link_id: str) -> Dict[str, Any]:
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(PaymentLink).where(PaymentLink.id == payment_link_id)
            )
            link = result.scalar_one_or_none()
            if link:
                return {"status": link.status, "paid_at": str(link.paid_at) if link.paid_at else None}
            return {"status": "not_found"}


class RazorpayPaymentProvider:
    """Razorpay payment provider (optional — requires credentials)."""

    async def create_payment_link(
        self,
        amount: float,
        currency: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str],
        reference_id: str,
        description: str,
    ) -> Dict[str, Any]:
        import httpx
        import base64

        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise ValueError("Razorpay credentials not configured")

        auth = base64.b64encode(
            f"{settings.RAZORPAY_KEY_ID}:{settings.RAZORPAY_KEY_SECRET}".encode()
        ).decode()

        payload = {
            "amount": int(amount * 100),  # Razorpay uses paise
            "currency": currency,
            "description": description,
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "contact": customer_phone or "",
            },
            "notify": {"sms": False, "email": False},
            "callback_url": f"{settings.BACKEND_URL}/api/webhooks/razorpay",
            "callback_method": "get",
            "reference_id": reference_id,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.razorpay.com/v1/payment_links",
                json=payload,
                headers={"Authorization": f"Basic {auth}"},
            )
            resp.raise_for_status()
            data = resp.json()

        link_id = data["id"]
        url = data["short_url"]

        async with async_session() as session:
            payment_link = PaymentLink(
                recovery_case_id=reference_id,
                provider="razorpay",
                provider_link_id=link_id,
                url=url,
                amount=amount,
                currency=currency,
                description=description,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                status="created",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            )
            session.add(payment_link)
            await session.commit()

        return {
            "provider": "razorpay",
            "link_id": link_id,
            "url": url,
            "amount": amount,
            "currency": currency,
            "status": "created",
        }

    async def get_payment_status(self, payment_link_id: str) -> Dict[str, Any]:
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(PaymentLink).where(PaymentLink.provider_link_id == payment_link_id)
            )
            link = result.scalar_one_or_none()
            if link:
                return {"status": link.status, "paid_at": str(link.paid_at) if link.paid_at else None}
            return {"status": "not_found"}


def get_payment_provider() -> MockPaymentProvider | RazorpayPaymentProvider:
    """Factory: returns appropriate payment provider based on config."""
    if settings.PAYMENT_PROVIDER == "razorpay":
        return RazorpayPaymentProvider()
    return MockPaymentProvider()
