"""Evidence record model and YAML serialization."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml


@dataclass
class DiffStat:
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    files: list[str] = field(default_factory=list)


@dataclass
class Artifact:
    type: str  # "jira", "confluence", "url"
    id: str
    url: str = ""
    title: str = ""
    extra: dict[str, str] = field(default_factory=dict)


@dataclass
class EvidenceRecord:
    version: int = 1
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    commit_sha: str = ""
    repo_path: str = ""
    repo_url: str = ""
    branch: str = ""
    diff_stat: DiffStat = field(default_factory=DiffStat)
    description: str = ""
    artifacts: list[Artifact] = field(default_factory=list)
    author_display_name: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "id": self.id,
            "commit_sha": self.commit_sha,
            "repo_path": self.repo_path,
            "repo_url": self.repo_url,
            "branch": self.branch,
            "diff_stat": {
                "files_changed": self.diff_stat.files_changed,
                "insertions": self.diff_stat.insertions,
                "deletions": self.diff_stat.deletions,
                "files": self.diff_stat.files,
            },
            "description": self.description,
            "artifacts": [
                {"type": a.type, "id": a.id, "url": a.url, "title": a.title, **a.extra}
                for a in self.artifacts
            ],
            "author_display_name": self.author_display_name,
            "created_at": self.created_at,
        }

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_dict(cls, data: dict) -> EvidenceRecord:
        ds = data.get("diff_stat", {})
        artifacts_raw = data.get("artifacts", [])
        artifacts = []
        for a in artifacts_raw:
            a = dict(a)
            extra = {k: v for k, v in a.items() if k not in ("type", "id", "url", "title")}
            artifacts.append(
                Artifact(
                    type=a.get("type", ""),
                    id=a.get("id", ""),
                    url=a.get("url", ""),
                    title=a.get("title", ""),
                    extra=extra,
                )
            )
        return cls(
            version=data.get("version", 1),
            id=data.get("id", str(uuid.uuid4())),
            commit_sha=data.get("commit_sha", ""),
            repo_path=data.get("repo_path", ""),
            repo_url=data.get("repo_url", ""),
            branch=data.get("branch", ""),
            diff_stat=DiffStat(
                files_changed=ds.get("files_changed", 0),
                insertions=ds.get("insertions", 0),
                deletions=ds.get("deletions", 0),
                files=ds.get("files", []),
            ),
            description=data.get("description", ""),
            artifacts=artifacts,
            author_display_name=data.get("author_display_name", ""),
            created_at=data.get("created_at", ""),
        )

    @classmethod
    def from_yaml(cls, text: str) -> EvidenceRecord:
        return cls.from_dict(yaml.safe_load(text))

    @classmethod
    def from_file(cls, path: Path) -> EvidenceRecord:
        return cls.from_yaml(path.read_text())

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        ts = self.created_at.replace(":", "-")
        short_sha = self.commit_sha[:8] if self.commit_sha else "manual"
        filename = f"{ts}_{short_sha}.yaml"
        path = directory / filename
        path.write_text(self.to_yaml())
        return path
