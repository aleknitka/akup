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


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def bootstrapped(client: AsyncClient) -> tuple[dict[str, Any], str]:
    """Bootstrap org + manager, return (manager_data, token)."""
    resp = await client.post(
        "/api/v1/auth/bootstrap",
        json={
            "org_name": "Test Org",
            "email": "manager@example.com",
            "password": "securepass123",
        },
    )
    assert resp.status_code == 201
    manager_data = resp.json()

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "manager@example.com", "password": "securepass123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return manager_data, token


@pytest.fixture
async def manager_token(bootstrapped: tuple[dict[str, Any], str]) -> str:
    _, token = bootstrapped
    return token


@pytest.fixture
async def user_token(client: AsyncClient, manager_token: str) -> str:
    """Create a regular user and return their token."""
    resp = await client.post(
        "/api/v1/users",
        json={"email": "user@example.com", "password": "userpass12345", "role": "user"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "userpass12345"},
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


@pytest.fixture
async def reporter_token(client: AsyncClient, manager_token: str) -> str:
    """Create a reporter user and return their token."""
    resp = await client.post(
        "/api/v1/users",
        json={"email": "reporter@example.com", "password": "reporterpass1", "role": "reporter"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "reporter@example.com", "password": "reporterpass1"},
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]
