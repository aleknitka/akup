"""Shared test fixtures."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repo with one commit (signing disabled)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=repo, capture_output=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, capture_output=True)
    # Disable any commit signing that might be configured globally
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"], cwd=repo, capture_output=True
    )
    subprocess.run(
        ["git", "config", "gpg.format", "openpgp"], cwd=repo, capture_output=True
    )

    (repo / "hello.py").write_text("print('hello')\n")
    subprocess.run(["git", "add", "hello.py"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    return repo
