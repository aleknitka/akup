"""Evidence recording: create evidence records from commits and manual input."""
from __future__ import annotations

from pathlib import Path

from akup.config import get_display_name, repo_evidence_dir
from akup.git_ops import get_commit_info, get_current_branch, get_diff_stat, get_remote_url
from akup.models import Artifact, DiffStat, EvidenceRecord


def record_commit(repo: Path, sha: str = "HEAD", description: str = "") -> EvidenceRecord:
    """Create an evidence record for a git commit."""
    commit = get_commit_info(repo, sha)
    diff = get_diff_stat(repo, sha)
    branch = get_current_branch(repo)
    remote_url = get_remote_url(repo)

    record = EvidenceRecord(
        commit_sha=commit.sha,
        repo_path=str(repo),
        repo_url=remote_url,
        branch=branch,
        diff_stat=DiffStat(
            files_changed=diff.files_changed,
            insertions=diff.insertions,
            deletions=diff.deletions,
            files=diff.files,
        ),
        description=description or commit.message,
        author_display_name=get_display_name(),
    )

    evidence_dir = repo_evidence_dir(repo)
    record.save(evidence_dir)
    return record


def record_manual(
    repo: Path,
    description: str,
    artifacts: list[dict] | None = None,
    commit_sha: str = "",
) -> EvidenceRecord:
    """Create a manual evidence record (not tied to a specific commit)."""
    remote_url = get_remote_url(repo)
    branch = get_current_branch(repo)

    parsed_artifacts = []
    for a in (artifacts or []):
        parsed_artifacts.append(
            Artifact(
                type=a.get("type", "url"),
                id=a.get("id", ""),
                url=a.get("url", ""),
                title=a.get("title", ""),
            )
        )

    record = EvidenceRecord(
        commit_sha=commit_sha,
        repo_path=str(repo),
        repo_url=remote_url,
        branch=branch,
        description=description,
        artifacts=parsed_artifacts,
        author_display_name=get_display_name(),
    )

    evidence_dir = repo_evidence_dir(repo)
    record.save(evidence_dir)
    return record


def list_evidence(repo: Path) -> list[EvidenceRecord]:
    """List all evidence records in a repo."""
    evidence_dir = repo_evidence_dir(repo)
    if not evidence_dir.exists():
        return []
    records = []
    for path in sorted(evidence_dir.glob("*.yaml")):
        if path.name == "config.yaml":
            continue
        try:
            records.append(EvidenceRecord.from_file(path))
        except Exception:
            continue
    return records
