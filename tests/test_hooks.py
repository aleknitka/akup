"""Tests for git hook management."""
from __future__ import annotations

from pathlib import Path

from akup.hooks import HOOK_MARKER, install_hook, is_hook_installed, uninstall_hook


def test_install_hook(git_repo: Path):
    path = install_hook(git_repo)
    assert path.exists()
    assert HOOK_MARKER in path.read_text()
    assert is_hook_installed(git_repo)


def test_install_idempotent(git_repo: Path):
    install_hook(git_repo)
    install_hook(git_repo)
    content = (git_repo / ".git" / "hooks" / "post-commit").read_text()
    assert content.count(HOOK_MARKER) == 1


def test_uninstall_hook(git_repo: Path):
    install_hook(git_repo)
    assert is_hook_installed(git_repo)

    result = uninstall_hook(git_repo)
    assert result is True
    assert not is_hook_installed(git_repo)


def test_uninstall_preserves_other_hooks(git_repo: Path):
    hook_path = git_repo / ".git" / "hooks" / "post-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text("#!/bin/sh\necho 'other hook'\n")

    install_hook(git_repo)
    assert "other hook" in hook_path.read_text()
    assert HOOK_MARKER in hook_path.read_text()

    uninstall_hook(git_repo)
    content = hook_path.read_text()
    assert "other hook" in content
    assert HOOK_MARKER not in content


def test_uninstall_no_hook(git_repo: Path):
    result = uninstall_hook(git_repo)
    assert result is False


def test_not_installed_by_default(git_repo: Path):
    assert not is_hook_installed(git_repo)
