from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


async def test_bootstrap_creates_org_and_manager(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/bootstrap",
        json={
            "org_name": "My Org",
            "email": "admin@example.com",
            "password": "securepass123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "admin@example.com"
    assert data["role"] == "manager"
    assert "display_name" in data
    assert data["is_active"] is True


async def test_bootstrap_only_once(
    client: AsyncClient, bootstrapped: tuple[dict[str, Any], str]
) -> None:
    resp = await client.post(
        "/api/v1/auth/bootstrap",
        json={
            "org_name": "Another Org",
            "email": "other@example.com",
            "password": "securepass123",
        },
    )
    assert resp.status_code == 409


async def test_login_valid(client: AsyncClient, bootstrapped: tuple[dict[str, Any], str]) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "manager@example.com", "password": "securepass123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(
    client: AsyncClient, bootstrapped: tuple[dict[str, Any], str]
) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "manager@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 401


async def test_me_endpoint(client: AsyncClient, manager_token: str) -> None:
    resp = await client.get("/api/v1/auth/me", headers=auth_header(manager_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "manager@example.com"
    assert data["role"] == "manager"


async def test_invalid_token(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me", headers=auth_header("invalid-token"))
    assert resp.status_code == 401


async def test_no_token(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
