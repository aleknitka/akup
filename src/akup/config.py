"""Configuration: per-repo (.akup/config.yaml) and global (~/.akup/config.yaml)."""
from __future__ import annotations

import random
from pathlib import Path

import yaml

AKUP_DIR = ".akup"
EVIDENCE_DIR = ".akup/evidence"
CONFIG_FILE = "config.yaml"

ADJECTIVES = [
    "Brave", "Bright", "Calm", "Clever", "Cool", "Daring", "Eager", "Fair",
    "Fast", "Fierce", "Gentle", "Grand", "Happy", "Keen", "Kind", "Lively",
    "Lucky", "Merry", "Mighty", "Noble", "Proud", "Quick", "Quiet", "Sharp",
    "Silent", "Smooth", "Steady", "Bold", "Swift", "Tall", "True", "Vivid",
    "Warm", "Wise", "Witty", "Agile", "Alert", "Crisp", "Deft", "Fresh",
]

ANIMALS = [
    "Falcon", "Otter", "Panda", "Raven", "Tiger", "Eagle", "Whale", "Heron",
    "Badger", "Crane", "Gecko", "Hound", "Koala", "Lemur", "Lynx", "Moose",
    "Owl", "Quail", "Robin", "Shark", "Stoat", "Viper", "Wolf", "Bison",
    "Finch", "Goose", "Hawk", "Jay", "Lark", "Mole", "Osprey", "Pike",
    "Seal", "Tern", "Wren", "Bear", "Dove", "Fox", "Hare", "Swan",
]


def global_config_dir() -> Path:
    return Path.home() / ".akup"


def global_config_path() -> Path:
    return global_config_dir() / CONFIG_FILE


def load_global_config() -> dict:
    path = global_config_path()
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def save_global_config(data: dict) -> None:
    path = global_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))


def get_display_name() -> str:
    """Get or generate the user's friendly display name."""
    config = load_global_config()
    name = config.get("display_name")
    if name:
        return name
    name = f"{random.choice(ADJECTIVES)} {random.choice(ANIMALS)}"
    config["display_name"] = name
    save_global_config(config)
    return name


def repo_akup_dir(repo_path: Path) -> Path:
    return repo_path / AKUP_DIR


def repo_evidence_dir(repo_path: Path) -> Path:
    return repo_path / EVIDENCE_DIR


def repo_config_path(repo_path: Path) -> Path:
    return repo_akup_dir(repo_path) / CONFIG_FILE


def load_repo_config(repo_path: Path) -> dict:
    path = repo_config_path(repo_path)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def save_repo_config(repo_path: Path, data: dict) -> None:
    path = repo_config_path(repo_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
