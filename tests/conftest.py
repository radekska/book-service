import asyncio
from typing import Generator, Callable, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.orm import mapper_registry
from database.session import engine, async_session, get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(mapper_registry.metadata.drop_all)
        await connection.run_sync(mapper_registry.metadata.create_all)
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture()
def app(override_get_db: Callable) -> FastAPI:
    from entrypoints.api import app

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://app") as async_client:
        async_client.headers["Content-Type"] = "application/json"
        yield async_client


@pytest_asyncio.fixture
async def authed_async_client(async_client: AsyncClient) -> AsyncGenerator:
    async_client.headers[
        "Authorization"
    ] = f"Bearer {AuthJWT().create_access_token(subject='test')}"
    yield async_client
