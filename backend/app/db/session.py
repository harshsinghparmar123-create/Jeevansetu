from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

import socket
from app.core.logging import logger

db_url = settings.DATABASE_URL
engine_kwargs = {"echo": False, "future": True}

def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False

# Fallback to local SQLite if PostgreSQL port is closed on localhost
use_sqlite = False
if "localhost" in db_url or "127.0.0.1" in db_url:
    if not is_port_open("127.0.0.1", 5432):
        use_sqlite = True

if use_sqlite:
    logger.warning("Local PostgreSQL on port 5432 is down. Falling back to SQLite: golden_minute.db")
    db_url = "sqlite+aiosqlite:///./golden_minute.db"
else:
    engine_kwargs["pool_pre_ping"] = True

# Create asynchronous engine
engine = create_async_engine(
    db_url,
    **engine_kwargs
)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency injection to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
