from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

engine = create_async_engine(
    settings.database_url, echo=settings.database_echo_log, future=True
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        yield session
        await session.commit()
