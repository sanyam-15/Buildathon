"""Database engine, session, and base model setup."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings

# Convert sqlite URL to async variant
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(db_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables and apply lightweight column migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # SQLite create_all does not add new columns to existing tables
        try:
            await conn.execute(text("ALTER TABLE recovery_cases ADD COLUMN segment VARCHAR"))
        except Exception:
            pass  # column already exists


async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session() as session:
        yield session
