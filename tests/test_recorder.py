"""Tests for evidence recording."""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from akup.recorder import list_evidence, record_commit, record_manual


@patch("akup.recorder.get_display_name", return_value="Brave Falcon")
def test_record_commit(mock_name, git_repo: Path):
    record = record_commit(git_repo)

    assert record.commit_sha
    assert len(record.commit_sha) == 40
    assert record.description == "Initial commit"
    assert record.diff_stat.files_changed == 1
    assert record.author_display_name == "Brave Falcon"

    evidence_dir = git_repo / ".akup" / "evidence"
    assert evidence_dir.exists()
    files = list(evidence_dir.glob("*.yaml"))
    assert len(files) == 1


@patch("akup.recorder.get_display_name", return_value="Quick Otter")
def test_record_commit_custom_description(mock_name, git_repo: Path):
    record = record_commit(git_repo, description="Custom creative work description")
    assert record.description == "Custom creative work description"


@patch("akup.recorder.get_display_name", return_value="Calm Panda")
def test_record_manual(mock_name, git_repo: Path):
    record = record_manual(
        git_repo,
        description="Wrote architecture document",
        artifacts=[
            {"type": "confluence", "id": "12345", "title": "Arch Doc"},
        ],
    )
    assert record.description == "Wrote architecture document"
    assert len(record.artifacts) == 1
    assert record.artifacts[0].type == "confluence"
    assert record.author_display_name == "Calm Panda"


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_list_evidence(mock_name, git_repo: Path):
    record_commit(git_repo)
    records = list_evidence(git_repo)
    assert len(records) == 1
    assert records[0].description == "Initial commit"


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_list_evidence_empty(mock_name, git_repo: Path):
    records = list_evidence(git_repo)
    assert records == []


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_multiple_records(mock_name, git_repo: Path):
    record_commit(git_repo)

    (git_repo / "second.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add second file"], cwd=git_repo, capture_output=True)
    record_commit(git_repo)

    records = list_evidence(git_repo)
    assert len(records) == 2
