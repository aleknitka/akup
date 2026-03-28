from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import auth_header

EVIDENCE_PAYLOAD = {
    "commit_sha": "abc1234def5678",
    "repo_url": "https://github.com/org/repo",
    "description": "Implemented new auth module",
    "evidence_date": "2026-03-10",
}


async def _create_evidence(client: AsyncClient, token: str) -> dict:
    resp = await client.post(
        "/api/v1/evidence",
        json=EVIDENCE_PAYLOAD,
        headers=auth_header(token),
    )
    assert resp.status_code == 201
    return resp.json()


# --- Creation ---


async def test_create_evidence(client: AsyncClient, manager_token: str) -> None:
    data = await _create_evidence(client, manager_token)
    assert data["commit_sha"] == "abc1234def5678"
    assert data["repo_url"] == "https://github.com/org/repo"
    assert data["description"] == "Implemented new auth module"
    assert data["ai_description"] is None
    assert data["removal_requested_at"] is None


async def test_user_creates_evidence(client: AsyncClient, user_token: str) -> None:
    data = await _create_evidence(client, user_token)
    assert data["commit_sha"] == "abc1234def5678"


async def test_reporter_cannot_create_evidence(
    client: AsyncClient, reporter_token: str
) -> None:
    resp = await client.post(
        "/api/v1/evidence",
        json=EVIDENCE_PAYLOAD,
        headers=auth_header(reporter_token),
    )
    assert resp.status_code == 403


# --- Listing / visibility ---


async def test_manager_sees_all_evidence(
    client: AsyncClient, manager_token: str, user_token: str
) -> None:
    await _create_evidence(client, manager_token)
    await _create_evidence(client, user_token)

    resp = await client.get("/api/v1/evidence", headers=auth_header(manager_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_user_sees_only_own(
    client: AsyncClient, manager_token: str, user_token: str
) -> None:
    await _create_evidence(client, manager_token)
    await _create_evidence(client, user_token)

    resp = await client.get("/api/v1/evidence", headers=auth_header(user_token))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1


async def test_reporter_sees_all_evidence(
    client: AsyncClient, manager_token: str, user_token: str, reporter_token: str
) -> None:
    await _create_evidence(client, manager_token)
    await _create_evidence(client, user_token)

    resp = await client.get("/api/v1/evidence", headers=auth_header(reporter_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# --- Get single ---


async def test_get_evidence(client: AsyncClient, manager_token: str) -> None:
    data = await _create_evidence(client, manager_token)
    resp = await client.get(
        f"/api/v1/evidence/{data['id']}", headers=auth_header(manager_token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == data["id"]


async def test_user_cannot_get_others_evidence(
    client: AsyncClient, manager_token: str, user_token: str
) -> None:
    data = await _create_evidence(client, manager_token)
    resp = await client.get(
        f"/api/v1/evidence/{data['id']}", headers=auth_header(user_token)
    )
    assert resp.status_code == 404


# --- Update ---


async def test_update_evidence(client: AsyncClient, manager_token: str) -> None:
    data = await _create_evidence(client, manager_token)
    resp = await client.put(
        f"/api/v1/evidence/{data['id']}",
        json={"description": "Updated description"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"


async def test_reporter_cannot_update(
    client: AsyncClient, manager_token: str, reporter_token: str
) -> None:
    data = await _create_evidence(client, manager_token)
    resp = await client.put(
        f"/api/v1/evidence/{data['id']}",
        json={"description": "Nope"},
        headers=auth_header(reporter_token),
    )
    assert resp.status_code == 403


# --- Delete ---


async def test_manager_deletes_evidence(client: AsyncClient, manager_token: str) -> None:
    data = await _create_evidence(client, manager_token)
    resp = await client.delete(
        f"/api/v1/evidence/{data['id']}", headers=auth_header(manager_token)
    )
    assert resp.status_code == 204

    resp = await client.get(
        f"/api/v1/evidence/{data['id']}", headers=auth_header(manager_token)
    )
    assert resp.status_code == 404


async def test_user_cannot_delete_directly(
    client: AsyncClient, user_token: str
) -> None:
    data = await _create_evidence(client, user_token)
    resp = await client.delete(
        f"/api/v1/evidence/{data['id']}", headers=auth_header(user_token)
    )
    assert resp.status_code == 403


# --- Removal request flow ---


async def test_request_and_approve_removal(
    client: AsyncClient, user_token: str, manager_token: str
) -> None:
    data = await _create_evidence(client, user_token)

    # User requests removal
    resp = await client.post(
        f"/api/v1/evidence/{data['id']}/request-removal",
        headers=auth_header(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["removal_requested_at"] is not None

    # Manager approves (deletes)
    resp = await client.post(
        f"/api/v1/evidence/{data['id']}/approve-removal",
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 204


async def test_request_and_cancel_removal(
    client: AsyncClient, user_token: str, manager_token: str
) -> None:
    data = await _create_evidence(client, user_token)

    resp = await client.post(
        f"/api/v1/evidence/{data['id']}/request-removal",
        headers=auth_header(user_token),
    )
    assert resp.status_code == 200

    resp = await client.post(
        f"/api/v1/evidence/{data['id']}/cancel-removal",
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    assert resp.json()["removal_requested_at"] is None


# --- Generate AI description ---


async def test_generate_description(client: AsyncClient, manager_token: str) -> None:
    data = await _create_evidence(client, manager_token)
    resp = await client.post(
        f"/api/v1/evidence/{data['id']}/generate-description",
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["ai_description"] is not None
    assert "abc1234d" in result["ai_description"]


# --- Date filter ---


async def test_list_evidence_filter_by_date(
    client: AsyncClient, manager_token: str
) -> None:
    await _create_evidence(client, manager_token)

    resp = await client.get(
        "/api/v1/evidence",
        params={"date_from": "2026-03-09", "date_to": "2026-03-11"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.get(
        "/api/v1/evidence",
        params={"date_from": "2026-03-11"},
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


# --- No auth ---


async def test_no_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/evidence")
    assert resp.status_code == 401
