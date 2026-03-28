"""Tests for configuration."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from akup.config import (
    get_display_name,
    load_repo_config,
    save_repo_config,
)


def test_save_and_load_repo_config(tmp_path: Path):
    config = {"jira": {"url": "https://jira.example.com", "project": "PROJ"}}
    save_repo_config(tmp_path, config)
    loaded = load_repo_config(tmp_path)
    assert loaded["jira"]["url"] == "https://jira.example.com"
    assert loaded["jira"]["project"] == "PROJ"


def test_load_missing_repo_config(tmp_path: Path):
    loaded = load_repo_config(tmp_path)
    assert loaded == {}


@patch("akup.config.global_config_path")
def test_get_display_name_generates_and_persists(mock_path, tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    mock_path.return_value = config_file

    name = get_display_name()
    assert " " in name  # "Adjective Animal" format

    # Second call should return the same name
    name2 = get_display_name()
    assert name == name2
