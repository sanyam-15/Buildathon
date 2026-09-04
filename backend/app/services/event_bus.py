"""In-memory event bus for SSE streaming and audit trail persistence.

Events are emitted by agents during LangGraph execution and streamed to 
the frontend in real-time via SSE. Each event is also persisted to the 
AuditLog table for full traceability.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, List, Optional
from collections import defaultdict

from app.database.database import async_session
from app.models.audit_log import AuditLog


class Event:
    """A single event emitted by an agent or system."""
    
    def __init__(
        self,
        case_id: str,
        event_type: str,
        agent: Optional[str] = None,
        message: str = "",
        metadata: Optional[dict] = None,
    ):
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.case_id = case_id
        self.event_type = event_type
        self.agent = agent
        self.message = message
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "case_id": self.case_id,
            "event_type": self.event_type,
            "agent": self.agent,
            "message": self.message,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventBus:
    """In-memory event bus with per-case-id subscriber queues."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._history: Dict[str, List[dict]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def emit(self, event: Event):
        """Emit an event to all subscribers of a case and persist to DB."""
        event_dict = event.to_dict()
        
        # Store in history
        self._history[event.case_id].append(event_dict)
        
        # Push to all subscriber queues for this case
        async with self._lock:
            for queue in self._subscribers.get(event.case_id, []):
                await queue.put(event_dict)
        
        # Persist to audit log
        try:
            async with async_session() as session:
                audit = AuditLog(
                    recovery_case_id=event.case_id,
                    event_type=event.event_type,
                    agent_name=event.agent,
                    message=event.message,
                    metadata_json=event.metadata,
                )
                session.add(audit)
                await session.commit()
        except Exception:
            pass  # Don't let audit persistence failure block agents

    async def subscribe(self, case_id: str) -> AsyncGenerator[dict, None]:
        """Subscribe to events for a case. Yields events as they arrive."""
        queue: asyncio.Queue = asyncio.Queue()
        
        async with self._lock:
            self._subscribers[case_id].append(queue)
        
        try:
            # First send history
            for event_dict in self._history.get(case_id, []):
                yield event_dict
            
            # Then stream new events
            while True:
                try:
                    event_dict = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event_dict
                    
                    # Stop streaming if case is complete
                    if event_dict.get("event_type") in (
                        "case_completed", "case_failed", "case_escalated", "revenue_recovered"
                    ):
                        break
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {"event_type": "keepalive", "case_id": case_id, "timestamp": datetime.now(timezone.utc).isoformat()}
        finally:
            async with self._lock:
                if case_id in self._subscribers:
                    self._subscribers[case_id].remove(queue)

    def get_history(self, case_id: str) -> List[dict]:
        """Get all events for a case."""
        return self._history.get(case_id, [])

    async def emit_simple(
        self,
        case_id: str,
        event_type: str,
        agent: Optional[str] = None,
        message: str = "",
        metadata: Optional[dict] = None,
    ):
        """Convenience method to emit without creating Event object manually."""
        event = Event(
            case_id=case_id,
            event_type=event_type,
            agent=agent,
            message=message,
            metadata=metadata,
        )
        await self.emit(event)


# Global singleton
event_bus = EventBus()
