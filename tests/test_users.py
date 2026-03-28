from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import auth_header


async def test_manager_creates_user(client: AsyncClient, manager_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "new@example.com", "password": "newpass12345", "role": "user"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "user"
    assert "display_name" in data
    assert len(data["display_name"]) > 0


async def test_manager_creates_reporter(client: AsyncClient, manager_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "rep@example.com", "password": "reporter1234", "role": "reporter"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "reporter"


async def test_user_cannot_create_user(client: AsyncClient, user_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "hacker@example.com", "password": "hackpass1234", "role": "user"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 403


async def test_reporter_cannot_create_user(client: AsyncClient, reporter_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "hacker@example.com", "password": "hackpass1234", "role": "user"},
        headers=auth_header(reporter_token),
    )
    assert resp.status_code == 403


async def test_list_users(client: AsyncClient, manager_token: str) -> None:
    resp = await client.get("/api/v1/users", headers=auth_header(manager_token))
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) >= 1


async def test_display_name_auto_assigned(client: AsyncClient, manager_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "test1@example.com", "password": "testpass12345", "role": "user"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 201
    name1 = resp.json()["display_name"]

    resp = await client.post(
        "/api/v1/users",
        json={"email": "test2@example.com", "password": "testpass12345", "role": "user"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 201
    name2 = resp.json()["display_name"]

    # Each user gets a unique display name
    assert name1 != name2
    # Names should be "Adjective Animal" format
    assert " " in name1
    assert " " in name2


async def test_change_role(client: AsyncClient, manager_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "role@example.com", "password": "rolepass12345", "role": "user"},
        headers=auth_header(manager_token),
    )
    user_id = resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/users/{user_id}/role",
        json={"role": "reporter"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "reporter"


async def test_deactivate_user(client: AsyncClient, manager_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        json={"email": "deact@example.com", "password": "deactpass1234", "role": "user"},
        headers=auth_header(manager_token),
    )
    user_id = resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/users/{user_id}", headers=auth_header(manager_token)
    )
    assert resp.status_code == 204


async def test_get_me(client: AsyncClient, user_token: str) -> None:
    resp = await client.get("/api/v1/users/me", headers=auth_header(user_token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"
