from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_async_session
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_session() -> AsyncIterator[AsyncSession]:
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def org_and_key(client: AsyncClient) -> tuple[dict[str, Any], str]:
    resp = await client.post("/api/v1/organizations", json={"name": "Test Org"})
    assert resp.status_code == 201
    data = resp.json()
    return data, data["api_key"]


@pytest.fixture
async def user_data(
    client: AsyncClient, org_and_key: tuple[dict[str, Any], str]
) -> dict[str, Any]:
    _, api_key = org_and_key
    resp = await client.post(
        "/api/v1/users",
        json={"name": "Jan Kowalski", "email": "jan@example.com"},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 201
    return resp.json()
