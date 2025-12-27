from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Convert postgres:// to postgresql+asyncpg://
database_url = settings.DATABASE_URL.replace(
    "postgres://", "postgresql+asyncpg://"
).replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(database_url, echo=settings.DEBUG)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        # Create tables (in production, use Alembic migrations)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
