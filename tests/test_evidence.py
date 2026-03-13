from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.fixture
async def evidence_data(
    client: AsyncClient,
    org_and_key: tuple[dict[str, Any], str],
    user_data: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    _, api_key = org_and_key
    resp = await client.post(
        "/api/v1/evidence",
        json={
            "commit_sha": "abc1234def5678",
            "repo_url": "https://github.com/org/repo",
            "description": "Implemented new auth module",
            "evidence_date": "2026-03-10",
            "created_by_user_id": user_data["id"],
        },
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 201
    return resp.json(), api_key


async def test_create_evidence(evidence_data: tuple[dict[str, Any], str]) -> None:
    data, _ = evidence_data
    assert data["commit_sha"] == "abc1234def5678"
    assert data["repo_url"] == "https://github.com/org/repo"
    assert data["description"] == "Implemented new auth module"
    assert data["ai_description"] is None


async def test_list_evidence(
    client: AsyncClient, evidence_data: tuple[dict[str, Any], str]
) -> None:
    _, api_key = evidence_data
    resp = await client.get("/api/v1/evidence", headers={"X-API-Key": api_key})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1


async def test_get_evidence(
    client: AsyncClient, evidence_data: tuple[dict[str, Any], str]
) -> None:
    data, api_key = evidence_data
    resp = await client.get(f"/api/v1/evidence/{data['id']}", headers={"X-API-Key": api_key})
    assert resp.status_code == 200
    assert resp.json()["id"] == data["id"]


async def test_update_evidence(
    client: AsyncClient, evidence_data: tuple[dict[str, Any], str]
) -> None:
    data, api_key = evidence_data
    resp = await client.put(
        f"/api/v1/evidence/{data['id']}",
        json={"description": "Updated description"},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"


async def test_delete_evidence(
    client: AsyncClient, evidence_data: tuple[dict[str, Any], str]
) -> None:
    data, api_key = evidence_data
    resp = await client.delete(f"/api/v1/evidence/{data['id']}", headers={"X-API-Key": api_key})
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/evidence/{data['id']}", headers={"X-API-Key": api_key})
    assert resp.status_code == 404


async def test_generate_description(
    client: AsyncClient, evidence_data: tuple[dict[str, Any], str]
) -> None:
    data, api_key = evidence_data
    resp = await client.post(
        f"/api/v1/evidence/{data['id']}/generate-description",
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["ai_description"] is not None
    assert "abc1234d" in result["ai_description"]


async def test_list_evidence_filter_by_date(
    client: AsyncClient, evidence_data: tuple[dict[str, Any], str]
) -> None:
    _, api_key = evidence_data
    resp = await client.get(
        "/api/v1/evidence",
        params={"date_from": "2026-03-09", "date_to": "2026-03-11"},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.get(
        "/api/v1/evidence",
        params={"date_from": "2026-03-11"},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


async def test_invalid_api_key(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/evidence", headers={"X-API-Key": "invalid-key"})
    assert resp.status_code == 401
