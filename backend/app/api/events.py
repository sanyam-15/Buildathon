"""Server-Sent Events (SSE) endpoint."""

import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.services.event_bus import event_bus

router = APIRouter()


@router.get("/{case_id}/stream")
async def stream_recovery_events(case_id: str, request: Request):
    """Stream real-time events for a recovery case using SSE."""

    async def event_generator():
        try:
            async for event_dict in event_bus.subscribe(case_id):
                if await request.is_disconnected():
                    break
                yield {
                    "event": "message",
                    "id": event_dict.get("event_id", ""),
                    "data": json.dumps(event_dict),
                }
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
