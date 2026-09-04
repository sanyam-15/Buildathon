"""Recovery API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.events import RecoveryEventInput, BatchRecoveryInput
from app.schemas.recovery import RecoveryCaseResponse, BatchResult
from app.services.recovery_service import start_recovery, get_case, start_batch_recovery

router = APIRouter()


@router.post("/start", response_model=dict)
async def trigger_recovery(event: RecoveryEventInput):
    """Trigger a new recovery workflow."""
    return await start_recovery(event)


@router.get("/{case_id}", response_model=RecoveryCaseResponse)
async def get_recovery_case(case_id: str):
    """Get details of a specific recovery case."""
    case = await get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")
    return case


@router.post("/batch", response_model=BatchResult)
async def trigger_batch_recovery(batch_input: BatchRecoveryInput):
    """Trigger a batch of recovery events."""
    return await start_batch_recovery(batch_input)
