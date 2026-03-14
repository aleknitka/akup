from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".akup"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict[str, str]:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save_config(data: dict[str, str]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2) + "\n")


def get_api_url() -> str:
    config = load_config()
    url = config.get("api_url")
    if not url:
        from rich.console import Console

        Console().print("[red]API URL not configured. Run 'akup init' first.[/red]")
        raise SystemExit(1)
    return url


def get_api_key() -> str:
    config = load_config()
    key = config.get("api_key")
    if not key:
        from rich.console import Console

        Console().print("[red]API key not configured. Run 'akup init' first.[/red]")
        raise SystemExit(1)
    return key
