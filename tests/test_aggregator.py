"""Tests for end-of-day aggregation."""
from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path
from unittest.mock import patch

from akup.aggregator import build_daily_report, collect_daily_evidence, save_daily_report
from akup.recorder import record_commit


def _make_repo(tmp_path: Path, name: str) -> Path:
    repo = tmp_path / name
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "gpg.format", "openpgp"], cwd=repo, capture_output=True)
    (repo / "file.py").write_text(f"# {name}\n")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", f"Init {name}"], cwd=repo, capture_output=True, check=True)
    return repo


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_collect_daily_evidence(mock_name, git_repo: Path):
    record_commit(git_repo)

    records = collect_daily_evidence([git_repo], target_date=date.today())
    assert len(records) == 1


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_collect_filters_by_date(mock_name, git_repo: Path):
    record_commit(git_repo)

    records = collect_daily_evidence([git_repo], target_date=date(2020, 1, 1))
    assert len(records) == 0


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_build_daily_report(mock_name, git_repo: Path):
    record_commit(git_repo)
    records = collect_daily_evidence([git_repo])
    report = build_daily_report(records)

    assert report["total_records"] == 1
    assert report["date"] == date.today().isoformat()
    assert len(report["records"]) == 1


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_save_daily_report(mock_name, git_repo: Path, tmp_path: Path):
    record_commit(git_repo)
    records = collect_daily_evidence([git_repo])
    report = build_daily_report(records)

    evidence_repo = tmp_path / "evidence-repo"
    path = save_daily_report(report, evidence_repo)

    assert path.exists()
    assert "reports" in str(path)
    assert date.today().isoformat() in path.name


@patch("akup.recorder.get_display_name", return_value="Test User")
def test_multiple_repos(mock_name, tmp_path: Path):
    repos = [_make_repo(tmp_path, f"repo{i}") for i in range(2)]
    for repo in repos:
        record_commit(repo)

    records = collect_daily_evidence(repos)
    assert len(records) == 2
