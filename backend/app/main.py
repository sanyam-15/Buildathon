"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.database import init_db
from app.api import recovery, dashboard, events, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    # Create DB tables
    await init_db()
    yield
    # Cleanup


app = FastAPI(
    title="Razorpay Relay Backend",
    description="Agentic AI Revenue Recovery Orchestrator",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recovery.router, prefix="/api/recovery", tags=["recovery"])
app.include_router(events.router, prefix="/api/recovery", tags=["events"])  # /api/recovery/{case_id}/stream
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
