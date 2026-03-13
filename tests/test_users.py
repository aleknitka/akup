from __future__ import annotations

from typing import Any

from httpx import AsyncClient


async def test_create_user(
    client: AsyncClient,
    org_and_key: tuple[dict[str, Any], str],
) -> None:
    _, api_key = org_and_key
    resp = await client.post(
        "/api/v1/users",
        json={"name": "Anna Nowak", "email": "anna@example.com"},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Anna Nowak"
    assert data["email"] == "anna@example.com"


async def test_list_users(
    client: AsyncClient,
    org_and_key: tuple[dict[str, Any], str],
    user_data: dict[str, Any],
) -> None:
    _, api_key = org_and_key
    resp = await client.get("/api/v1/users", headers={"X-API-Key": api_key})
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) == 1
    assert users[0]["name"] == "Jan Kowalski"


async def test_create_org_returns_api_key(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/organizations", json={"name": "New Company"})
    assert resp.status_code == 201
    data = resp.json()
    assert "api_key" in data
    assert len(data["api_key"]) > 20
