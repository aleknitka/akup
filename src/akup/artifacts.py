"""Artifact clients: Jira and Confluence integration for linking evidence."""
from __future__ import annotations

from dataclasses import dataclass

import httpx

from akup.config import load_repo_config
from akup.models import Artifact


@dataclass
class JiraConfig:
    url: str
    project: str
    email: str = ""
    token: str = ""


@dataclass
class ConfluenceConfig:
    url: str
    space: str
    email: str = ""
    token: str = ""


def _jira_config_from_repo(repo_config: dict) -> JiraConfig | None:
    jira = repo_config.get("jira")
    if not jira or not jira.get("url"):
        return None
    return JiraConfig(
        url=jira["url"].rstrip("/"),
        project=jira.get("project", ""),
        email=jira.get("email", ""),
        token=jira.get("token", ""),
    )


def _confluence_config_from_repo(repo_config: dict) -> ConfluenceConfig | None:
    conf = repo_config.get("confluence")
    if not conf or not conf.get("url"):
        return None
    return ConfluenceConfig(
        url=conf["url"].rstrip("/"),
        space=conf.get("space", ""),
        email=conf.get("email", ""),
        token=conf.get("token", ""),
    )


def _jira_auth(config: JiraConfig) -> httpx.Auth | None:
    if config.email and config.token:
        return httpx.BasicAuth(config.email, config.token)
    return None


def _confluence_auth(config: ConfluenceConfig) -> httpx.Auth | None:
    if config.email and config.token:
        return httpx.BasicAuth(config.email, config.token)
    return None


def fetch_jira_issue(config: JiraConfig, issue_id: str) -> Artifact:
    """Fetch a Jira issue and return it as an Artifact."""
    url = f"{config.url}/rest/api/2/issue/{issue_id}"
    try:
        resp = httpx.get(url, auth=_jira_auth(config), timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        return Artifact(
            type="jira",
            id=issue_id,
            url=f"{config.url}/browse/{issue_id}",
            title=data.get("fields", {}).get("summary", ""),
            extra={"status": data.get("fields", {}).get("status", {}).get("name", "")},
        )
    except Exception as e:
        return Artifact(
            type="jira",
            id=issue_id,
            url=f"{config.url}/browse/{issue_id}",
            title="",
            extra={"error": str(e)},
        )


def fetch_confluence_page(config: ConfluenceConfig, page_id: str) -> Artifact:
    """Fetch a Confluence page and return it as an Artifact."""
    url = f"{config.url}/rest/api/content/{page_id}"
    try:
        resp = httpx.get(
            url,
            auth=_confluence_auth(config),
            params={"expand": "version"},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return Artifact(
            type="confluence",
            id=page_id,
            url=f"{config.url}/pages/{page_id}",
            title=data.get("title", ""),
            extra={"version": str(data.get("version", {}).get("number", ""))},
        )
    except Exception as e:
        return Artifact(
            type="confluence",
            id=page_id,
            url=f"{config.url}/pages/{page_id}",
            title="",
            extra={"error": str(e)},
        )


def resolve_artifact(repo_config: dict, artifact_type: str, artifact_id: str) -> Artifact:
    """Resolve an artifact reference to a full Artifact with metadata."""
    if artifact_type == "jira":
        config = _jira_config_from_repo(repo_config)
        if config:
            return fetch_jira_issue(config, artifact_id)
        return Artifact(type="jira", id=artifact_id)

    if artifact_type == "confluence":
        config = _confluence_config_from_repo(repo_config)
        if config:
            return fetch_confluence_page(config, artifact_id)
        return Artifact(type="confluence", id=artifact_id)

    # Generic URL artifact
    return Artifact(type=artifact_type, id=artifact_id, url=artifact_id)
