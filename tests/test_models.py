"""Tests for evidence model and YAML serialization."""
from __future__ import annotations

from pathlib import Path

import yaml

from akup.models import Artifact, DiffStat, EvidenceRecord


def test_evidence_to_dict():
    record = EvidenceRecord(
        id="test-id",
        commit_sha="abc1234def5678",
        repo_path="/tmp/repo",
        repo_url="https://github.com/org/repo",
        branch="main",
        diff_stat=DiffStat(files_changed=3, insertions=47, deletions=12, files=["a.py", "b.py"]),
        description="Implemented auth module",
        artifacts=[
            Artifact(type="jira", id="PROJ-123", url="https://jira.example.com/browse/PROJ-123",
                     title="Auth module"),
        ],
        author_display_name="Brave Falcon",
        created_at="2026-03-28T09:15:00",
    )
    d = record.to_dict()
    assert d["commit_sha"] == "abc1234def5678"
    assert d["diff_stat"]["files_changed"] == 3
    assert d["diff_stat"]["files"] == ["a.py", "b.py"]
    assert len(d["artifacts"]) == 1
    assert d["artifacts"][0]["type"] == "jira"
    assert d["author_display_name"] == "Brave Falcon"


def test_evidence_yaml_roundtrip():
    record = EvidenceRecord(
        id="roundtrip-id",
        commit_sha="deadbeef",
        description="Test roundtrip",
        diff_stat=DiffStat(files_changed=1, insertions=5, deletions=0, files=["test.py"]),
        author_display_name="Quick Otter",
        created_at="2026-03-28T10:00:00",
    )
    yaml_str = record.to_yaml()
    loaded = EvidenceRecord.from_yaml(yaml_str)

    assert loaded.id == "roundtrip-id"
    assert loaded.commit_sha == "deadbeef"
    assert loaded.description == "Test roundtrip"
    assert loaded.diff_stat.files_changed == 1
    assert loaded.diff_stat.files == ["test.py"]
    assert loaded.author_display_name == "Quick Otter"


def test_evidence_save_and_load(tmp_path: Path):
    record = EvidenceRecord(
        id="save-test",
        commit_sha="abc12345",
        description="Save test",
        created_at="2026-03-28T09-15-00",
    )
    path = record.save(tmp_path / "evidence")
    assert path.exists()
    assert path.suffix == ".yaml"

    loaded = EvidenceRecord.from_file(path)
    assert loaded.id == "save-test"
    assert loaded.commit_sha == "abc12345"


def test_evidence_from_dict_with_extra_artifact_fields():
    data = {
        "version": 1,
        "id": "extra-test",
        "commit_sha": "aaa",
        "artifacts": [
            {"type": "jira", "id": "X-1", "url": "", "title": "Ticket", "status": "Done"},
        ],
        "created_at": "2026-03-28T12:00:00",
    }
    record = EvidenceRecord.from_dict(data)
    assert record.artifacts[0].extra["status"] == "Done"

    # Roundtrip preserves extra
    d = record.to_dict()
    assert d["artifacts"][0]["status"] == "Done"
