"""Git operations: read commit info, diff stats, repo metadata."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


def _run(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        args, capture_output=True, text=True, cwd=cwd, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"git command failed: {' '.join(args)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def find_repo_root(path: Path | None = None) -> Path:
    cwd = path or Path.cwd()
    root = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    return Path(root)


def get_current_branch(repo: Path) -> str:
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo)


def get_remote_url(repo: Path) -> str:
    try:
        return _run(["git", "remote", "get-url", "origin"], cwd=repo)
    except RuntimeError:
        return ""


@dataclass
class CommitInfo:
    sha: str
    message: str
    author_name: str
    author_email: str
    timestamp: str


def get_commit_info(repo: Path, sha: str = "HEAD") -> CommitInfo:
    fmt = "%H%n%s%n%an%n%ae%n%aI"
    output = _run(["git", "log", "-1", f"--format={fmt}", sha], cwd=repo)
    lines = output.split("\n")
    return CommitInfo(
        sha=lines[0],
        message=lines[1] if len(lines) > 1 else "",
        author_name=lines[2] if len(lines) > 2 else "",
        author_email=lines[3] if len(lines) > 3 else "",
        timestamp=lines[4] if len(lines) > 4 else "",
    )


@dataclass
class DiffStatResult:
    files_changed: int
    insertions: int
    deletions: int
    files: list[str]


def get_diff_stat(repo: Path, sha: str = "HEAD") -> DiffStatResult:
    # Use --root to handle initial commits (no parent)
    files_output = _run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha], cwd=repo
    )
    files = [f for f in files_output.split("\n") if f]

    stat_output = _run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--numstat", "-r", sha], cwd=repo
    )
    insertions = 0
    deletions = 0
    for line in stat_output.split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            try:
                insertions += int(parts[0])
            except ValueError:
                pass
            try:
                deletions += int(parts[1])
            except ValueError:
                pass

    return DiffStatResult(
        files_changed=len(files),
        insertions=insertions,
        deletions=deletions,
        files=files,
    )


def get_head_sha(repo: Path) -> str:
    return _run(["git", "rev-parse", "HEAD"], cwd=repo)


def stage_and_commit(repo: Path, paths: list[str], message: str) -> str:
    for p in paths:
        _run(["git", "add", p], cwd=repo)
    _run(["git", "commit", "-m", message, "--no-verify"], cwd=repo)
    return get_head_sha(repo)
