"""Configuration settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./recoverai.db"
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None
    
    # LangSmith
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "razorpay-relay"
    
    # Payment Provider
    PAYMENT_PROVIDER: str = "mock"
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = None
    
    # Communication Provider
    COMMUNICATION_PROVIDER: str = "mock"
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "onboarding@resend.dev"
    
    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
