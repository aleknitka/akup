"""Tests for git operations using temporary repos."""
from __future__ import annotations

import subprocess
from pathlib import Path

from akup.git_ops import (
    find_repo_root,
    get_commit_info,
    get_current_branch,
    get_diff_stat,
    get_head_sha,
    get_remote_url,
)


def test_find_repo_root(git_repo: Path):
    root = find_repo_root(git_repo)
    assert root == git_repo


def test_get_current_branch(git_repo: Path):
    branch = get_current_branch(git_repo)
    assert branch in ("main", "master")


def test_get_remote_url_empty(git_repo: Path):
    url = get_remote_url(git_repo)
    assert url == ""


def test_get_commit_info(git_repo: Path):
    info = get_commit_info(git_repo)
    assert info.message == "Initial commit"
    assert info.author_email == "test@test.com"
    assert len(info.sha) == 40


def test_get_diff_stat(git_repo: Path):
    stat = get_diff_stat(git_repo)
    assert stat.files_changed == 1
    assert stat.files == ["hello.py"]
    assert stat.insertions == 1
    assert stat.deletions == 0


def test_get_head_sha(git_repo: Path):
    sha = get_head_sha(git_repo)
    assert len(sha) == 40


def test_diff_stat_multiple_files(git_repo: Path):
    (git_repo / "a.py").write_text("x = 1\ny = 2\n")
    (git_repo / "b.py").write_text("z = 3\n")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add two files"], cwd=git_repo, capture_output=True)

    stat = get_diff_stat(git_repo)
    assert stat.files_changed == 2
    assert set(stat.files) == {"a.py", "b.py"}
    assert stat.insertions == 3
