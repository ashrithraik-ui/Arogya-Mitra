"""
ArogyaMitra AI — Database Setup
SQLAlchemy async engine with SQLite.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings


# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.AROGYA_DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

# ── Session factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── Base declarative model ────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency — yields an async DB session ───────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency: yields a database session and ensures it is closed."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Schema initializer ────────────────────────────────────────────────────────
async def init_db() -> None:
    """Create all tables if they do not already exist."""
    # Import all models so SQLAlchemy discovers them before create_all
    from backend.models import patient, doctor, consultation, timeline  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
