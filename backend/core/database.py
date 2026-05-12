from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from backend.core.config import get_settings

settings = get_settings()

def _async_database_url(url: str) -> str:
    """Convert common sync URLs to SQLAlchemy async driver URLs."""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


database_url = _async_database_url(settings.DATABASE_URL)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "connect_args": connect_args,
}
if not database_url.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "poolclass": NullPool if settings.ENVIRONMENT == "test" else None,
        }
    )

engine = create_async_engine(database_url, **engine_kwargs)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Get database session."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    import backend.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
