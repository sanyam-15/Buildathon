"""Communication provider abstraction with Mock and Resend implementations."""

from typing import Optional, Protocol, Dict, Any

from app.config import settings
from app.database.database import async_session
from app.models.audit_log import Communication


class CommunicationProvider(Protocol):
    """Protocol for communication providers."""

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        recovery_case_id: str,
    ) -> Dict[str, Any]:
        ...

    async def send_whatsapp(
        self,
        recipient: str,
        message: str,
        recovery_case_id: str,
    ) -> Dict[str, Any]:
        ...


class MockCommunicationProvider:
    """Mock communication provider — stores messages in DB."""

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        recovery_case_id: str,
    ) -> Dict[str, Any]:
        async with async_session() as session:
            comm = Communication(
                recovery_case_id=recovery_case_id,
                channel="email",
                recipient=recipient,
                subject=subject,
                message=body,
                status="sent_mock",
            )
            session.add(comm)
            await session.commit()

        return {
            "provider": "mock",
            "channel": "email",
            "recipient": recipient,
            "subject": subject,
            "status": "sent_mock",
        }

    async def send_whatsapp(
        self,
        recipient: str,
        message: str,
        recovery_case_id: str,
    ) -> Dict[str, Any]:
        async with async_session() as session:
            comm = Communication(
                recovery_case_id=recovery_case_id,
                channel="whatsapp",
                recipient=recipient,
                subject=None,
                message=message,
                status="sent_mock",
            )
            session.add(comm)
            await session.commit()

        return {
            "provider": "mock",
            "channel": "whatsapp",
            "recipient": recipient,
            "status": "sent_mock",
        }


class ResendCommunicationProvider:
    """Resend email provider for real email delivery."""

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        recovery_case_id: str,
    ) -> Dict[str, Any]:
        import httpx

        if not settings.RESEND_API_KEY:
            raise ValueError("Resend API key not configured")

        # Build HTML email
        html_body = body.replace("\n", "<br>")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.EMAIL_FROM,
                    "to": [recipient],
                    "subject": subject,
                    "html": f"<div style='font-family: sans-serif; max-width: 600px; margin: 0 auto;'>{html_body}</div>",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        async with async_session() as session:
            comm = Communication(
                recovery_case_id=recovery_case_id,
                channel="email",
                recipient=recipient,
                subject=subject,
                message=body,
                status="sent",
            )
            session.add(comm)
            await session.commit()

        return {
            "provider": "resend",
            "channel": "email",
            "recipient": recipient,
            "subject": subject,
            "status": "sent",
            "email_id": data.get("id"),
        }

    async def send_whatsapp(
        self,
        recipient: str,
        message: str,
        recovery_case_id: str,
    ) -> Dict[str, Any]:
        # WhatsApp not available through Resend — gracefully degrade
        return await MockCommunicationProvider().send_whatsapp(
            recipient=recipient,
            message=message,
            recovery_case_id=recovery_case_id,
        )


def get_communication_provider() -> MockCommunicationProvider | ResendCommunicationProvider:
    """Factory: returns appropriate communication provider."""
    if settings.COMMUNICATION_PROVIDER == "resend":
        return ResendCommunicationProvider()
    return MockCommunicationProvider()
