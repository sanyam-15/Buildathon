"""Dashboard API endpoints."""

from fastapi import APIRouter
from typing import List

from app.schemas.recovery import DashboardStats
from app.services.recovery_service import get_dashboard_stats, get_all_cases

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    """Get overall dashboard statistics."""
    return await get_dashboard_stats()


@router.get("/cases", response_model=List[dict])
async def get_cases():
    """Get all recovery cases."""
    return await get_all_cases()
