from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo_log,
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
